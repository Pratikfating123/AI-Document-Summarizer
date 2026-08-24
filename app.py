import os
import time
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from config import Config
from summarizer.text_extractor import extract_document_text
from summarizer.summarizer import summarize_text
from summarizer.statistics import calculate_statistics

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "AI Document Summarizer"})


@app.route("/summarize", methods=["POST"])
def summarize():
    start = time.perf_counter()

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No document was uploaded."}), 400

    uploaded = request.files["file"]

    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "error": "Please select a document."}), 400

    if not allowed_file(uploaded.filename):
        allowed = ", ".join(sorted(app.config["ALLOWED_EXTENSIONS"]).upper())
        return jsonify({
            "success": False,
            "error": f"Unsupported file type. Allowed formats: {allowed}."
        }), 400

    filename = secure_filename(uploaded.filename)
    if not filename:
        return jsonify({"success": False, "error": "Invalid filename."}), 400

    saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        uploaded.save(saved_path)
        text = extract_document_text(saved_path)

        if not text or not text.strip():
            return jsonify({
                "success": False,
                "error": "The document does not contain readable text."
            }), 400

        length = request.form.get("length", "medium").lower()
        if length not in {"short", "medium", "long"}:
            length = "medium"

        summary = summarize_text(text, length=length)

        if not summary.strip():
            return jsonify({
                "success": False,
                "error": "The document was readable, but no meaningful summary could be generated."
            }), 422

        stats = calculate_statistics(text, summary)
        processing_time = round(time.perf_counter() - start, 3)

        return jsonify({
            "success": True,
            "filename": filename,
            "summary": summary,
            "original_text": text,
            "statistics": stats,
            "processing_time": processing_time
        })

    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("Document processing failed")
        return jsonify({
            "success": False,
            "error": "The document could not be processed. Please try another file."
        }), 500
    finally:
        try:
            if os.path.exists(saved_path):
                os.remove(saved_path)
        except OSError:
            pass


@app.route("/download", methods=["POST"])
def download_summary():
    data = request.get_json(silent=True) or {}
    summary = str(data.get("summary", "")).strip()
    filename = secure_filename(str(data.get("filename", "document")))

    if not summary:
        return jsonify({"success": False, "error": "No summary is available."}), 400

    base = os.path.splitext(filename)[0] or "document"
    output_name = f"{base}_summary.txt"
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_name)

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("AI DOCUMENT SUMMARIZER\n")
            file.write("=" * 24 + "\n\n")
            file.write(summary)
            file.write("\n")

        response = send_file(
            output_path,
            as_attachment=True,
            download_name=output_name,
            mimetype="text/plain"
        )
        response.call_on_close(lambda: _remove_file(output_path))
        return response
    except OSError:
        return jsonify({
            "success": False,
            "error": "The summary could not be prepared for download."
        }), 500


def _remove_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@app.errorhandler(413)
def too_large(_error):
    return jsonify({
        "success": False,
        "error": "The file is too large. Maximum allowed size is 10 MB."
    }), 413


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/") or request.path in {"/summarize", "/download"}:
        return jsonify({"success": False, "error": "Endpoint not found."}), 404
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
