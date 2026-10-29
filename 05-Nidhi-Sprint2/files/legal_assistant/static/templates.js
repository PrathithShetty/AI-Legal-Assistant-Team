// Template page: copy or download the generated document (FR-19).
(function () {
  "use strict";

  function setupDocumentTools() {
    const doc = document.getElementById("generated-document");
    if (!doc) return;
    const status = document.getElementById("document-status");
    document.getElementById("copy-document").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(doc.value);
        status.textContent = "Copied to clipboard.";
      } catch (_) {
        doc.select();
        status.textContent = "Press Ctrl+C to copy.";
      }
    });
    document.getElementById("download-document").addEventListener("click", (e) => {
      const blob = new Blob([doc.value], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = (e.currentTarget.dataset.filename || "document") + ".txt";
      link.click();
      URL.revokeObjectURL(link.href);
    });
  }

  setupDocumentTools();
})();
