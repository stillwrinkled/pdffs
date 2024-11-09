document.addEventListener('DOMContentLoaded', () => {
    const pdfContainer = document.getElementById('pdf-form-container');

    async function renderPDF() {
        const url = pdfContainer.dataset.pdfUrl;
        const loadingTask = pdfjsLib.getDocument(url);
        const pdf = await loadingTask.promise;

        for (let i = 0; i < pdf.numPages; i++) {
            const page = await pdf.getPage(i + 1);
            const viewport = page.getViewport({ scale: 1.5 });
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            pdfContainer.appendChild(canvas);

            const context = canvas.getContext('2d');
            await page.render({ canvasContext: context, viewport }).promise;

            // Add input fields on top of PDF for each form field.
            // Customize this part with positioning for keyboard/mouse interaction
        }
    }

    renderPDF();
});
