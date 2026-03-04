const form = document.getElementById("convert-form");
const fileInput = document.getElementById("file-input");
const fileMeta = document.getElementById("file-meta");
const convertButton = document.getElementById("convert-button");
const statusBox = document.getElementById("status");

function setStatus(kind, message) {
  statusBox.className = `status ${kind}`;
  statusBox.textContent = message;
}

function formatBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) {
    fileMeta.textContent = "No file selected.";
    setStatus("idle", "Waiting for file.");
    return;
  }

  fileMeta.textContent = `${file.name} (${formatBytes(file.size)})`;
  setStatus("idle", "Ready to convert.");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    setStatus("error", "Choose an MP4 file first.");
    return;
  }

  convertButton.disabled = true;
  setStatus("busy", "Converting locally. This may take a moment.");

  try {
    const response = await fetch("/api/convert/mp4-to-wav", {
      method: "POST",
      headers: {
        "Content-Type": file.type || "video/mp4"
      },
      body: file
    });

    if (!response.ok) {
      let message = "Conversion failed.";

      try {
        const payload = await response.json();
        message = payload.error || message;
      } catch (error) {
        message = "Conversion failed.";
      }

      throw new Error(message);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    const baseName = file.name.replace(/\.[^.]+$/, "") || "converted";

    anchor.href = url;
    anchor.download = `${baseName}.wav`;
    anchor.click();
    URL.revokeObjectURL(url);

    setStatus("success", "Done. Your WAV download has started.");
  } catch (error) {
    setStatus("error", error.message);
  } finally {
    convertButton.disabled = false;
  }
});
