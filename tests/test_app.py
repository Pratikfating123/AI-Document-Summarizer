import io
from app import app


def test_home():
    app.config["TESTING"] = True
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_upload():
    app.config["TESTING"] = True
    client = app.test_client()
    response = client.post(
        "/summarize",
        data={"file": (io.BytesIO(b"not supported"), "test.exe")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False
