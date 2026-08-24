const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const filePreview = document.getElementById("filePreview");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFileBtn = document.getElementById("removeFileBtn");
const summarizeBtn = document.getElementById("summarizeBtn");
const summaryLength = document.getElementById("summaryLength");
const processingBox = document.getElementById("processingBox");
const processingMessage = document.getElementById("processingMessage");
const processingPercent = document.getElementById("processingPercent");
const processingProgress = document.getElementById("processingProgress");
const resultsSection = document.getElementById("resultsSection");
const statsGrid = document.getElementById("statsGrid");
const summaryText = document.getElementById("summaryText");
const originalText = document.getElementById("originalText");
const lengthBadge = document.getElementById("lengthBadge");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const clearBtn = document.getElementById("clearBtn");
const againBtn = document.getElementById("againBtn");
const originalToggle = document.getElementById("originalToggle");
const originalTextWrapper = document.getElementById("originalTextWrapper");
const originalChevron = document.getElementById("originalChevron");
const alertBox = document.getElementById("alertBox");
const toast = document.getElementById("toast");

let selectedFile = null;
let latestSummary = "";
let latestFilename = "";

const MAX_SIZE = 10 * 1024 * 1024;
const ALLOWED = ["pdf", "docx", "txt"];

function showAlert(message, type = "danger") {
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    alertBox.classList.remove("d-none");
    window.scrollTo({ top: alertBox.getBoundingClientRect().top + window.scrollY - 90, behavior: "smooth" });
}

function hideAlert() {
    alertBox.classList.add("d-none");
}

function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2400);
}

function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function validateFile(file) {
    if (!file) return "Please select a document.";
    const extension = file.name.split(".").pop().toLowerCase();

    if (!ALLOWED.includes(extension)) {
        return "Unsupported file type. Please choose a PDF, DOCX, or TXT file.";
    }

    if (file.size > MAX_SIZE) {
        return "The selected file is larger than 10 MB.";
    }

    return null;
}

function setFile(file) {
    const error = validateFile(file);
    if (error) {
        showAlert(error);
        resetFile();
        return;
    }

    hideAlert();
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);
    filePreview.classList.remove("d-none");
    dropZone.classList.add("d-none");
    summarizeBtn.disabled = false;
}

function resetFile() {
    selectedFile = null;
    fileInput.value = "";
    filePreview.classList.add("d-none");
    dropZone.classList.remove("d-none");
    summarizeBtn.disabled = true;
}

browseBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) setFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("dragover");
    });
});

dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];
    if (file) setFile(file);
});

removeFileBtn.addEventListener("click", resetFile);

function setProcessing(message, percent) {
    processingMessage.textContent = message;
    processingPercent.textContent = `${percent}%`;
    processingProgress.style.width = `${percent}%`;
}

async function generateSummary() {
    if (!selectedFile) {
        showAlert("Please select a document first.");
        return;
    }

    hideAlert();
    summarizeBtn.disabled = true;
    document.querySelector(".button-text").classList.add("d-none");
    document.querySelector(".button-loading").classList.remove("d-none");
    processingBox.classList.remove("d-none");
    resultsSection.classList.add("d-none");

    setProcessing("Extracting document text...", 20);
    await new Promise(resolve => setTimeout(resolve, 350));

    setProcessing("Analyzing document with NLP...", 48);
    await new Promise(resolve => setTimeout(resolve, 350));

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("length", summaryLength.value);

    try {
        setProcessing("Ranking important sentences...", 72);

        const response = await fetch("/summarize", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Unable to generate summary.");
        }

        setProcessing("Finalizing summary...", 92);
        await new Promise(resolve => setTimeout(resolve, 300));

        latestSummary = data.summary;
        latestFilename = data.filename;

        renderResults(data);
        setProcessing("Summary ready.", 100);
        showToast("Summary generated successfully.");
    } catch (error) {
        showAlert(error.message || "Something went wrong while processing the document.");
    } finally {
        summarizeBtn.disabled = !selectedFile;
        document.querySelector(".button-text").classList.remove("d-none");
        document.querySelector(".button-loading").classList.add("d-none");
        setTimeout(() => processingBox.classList.add("d-none"), 700);
    }
}

function renderResults(data) {
    const s = data.statistics;
    const stats = [
        ["Original Words", s.original_words.toLocaleString()],
        ["Summary Words", s.summary_words.toLocaleString()],
        ["Compression", `${s.compression_percentage}%`],
        ["Reading Time", `${s.reading_time} min`],
        ["Processing", `${data.processing_time}s`]
    ];

    statsGrid.innerHTML = stats.map(([label, value]) => `
        <div class="stat-card">
            <div class="stat-label">${label}</div>
            <div class="stat-value">${value}</div>
        </div>
    `).join("");

    summaryText.textContent = data.summary;
    originalText.textContent = data.original_text;
    lengthBadge.textContent = summaryLength.options[summaryLength.selectedIndex].text.split(",")[0];

    resultsSection.classList.remove("d-none");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

copyBtn.addEventListener("click", async () => {
    if (!latestSummary) return;

    try {
        await navigator.clipboard.writeText(latestSummary);
        showToast("Summary copied to clipboard.");
    } catch {
        showAlert("Clipboard access was blocked by the browser.", "warning");
    }
});

downloadBtn.addEventListener("click", async () => {
    if (!latestSummary) return;

    try {
        const response = await fetch("/download", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                summary: latestSummary,
                filename: latestFilename
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || "Download failed.");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = `${latestFilename.replace(/\.[^/.]+$/, "")}_summary.txt`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
        showToast("Summary downloaded.");
    } catch (error) {
        showAlert(error.message || "Could not download the summary.");
    }
});

originalToggle.addEventListener("click", () => {
    originalTextWrapper.classList.toggle("d-none");
    originalChevron.classList.toggle("fa-chevron-down");
    originalChevron.classList.toggle("fa-chevron-up");
});

function clearAll() {
    resetFile();
    latestSummary = "";
    latestFilename = "";
    resultsSection.classList.add("d-none");
    originalTextWrapper.classList.add("d-none");
    originalChevron.classList.add("fa-chevron-down");
    originalChevron.classList.remove("fa-chevron-up");
    hideAlert();
    window.scrollTo({ top: document.getElementById("summarizer").offsetTop - 90, behavior: "smooth" });
}

clearBtn.addEventListener("click", clearAll);
againBtn.addEventListener("click", generateSummary);
summarizeBtn.addEventListener("click", generateSummary);
