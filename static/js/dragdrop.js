document.addEventListener('DOMContentLoaded', setupDragDrop);

function setupDragDrop() {
    const dragDropZones = document.querySelectorAll('.drag-drop-zone');

    dragDropZones.forEach(zone => {
        const fileInput = zone.querySelector('input[type="file"]');
        const fileList = zone.querySelector('.file-list');
        const pdfPreview = document.getElementById('pdf-preview');

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFileSelection(e.dataTransfer.files, fileInput, fileList, pdfPreview);
            }
        });

        zone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            handleFileSelection(fileInput.files, fileInput, fileList, pdfPreview);
        });
    });
}

function handleFileSelection(files, fileInput, fileList, pdfPreview) {
    fileList.innerHTML = '';
    pdfPreview.innerHTML = '';

    const file = files[0];
    if (file && file.type === 'application/pdf') {
        const li = document.createElement('li');
        li.textContent = file.name;
        li.classList.add('selected-file');
        fileList.appendChild(li);

        const reader = new FileReader();
        reader.onload = function(e) {
            displayPDF(e.target.result, pdfPreview);
        };
        reader.readAsDataURL(file);
    } else {
        alert("Please upload a valid PDF file.");
        fileInput.value = '';  // Clear invalid file
    }
}

function displayPDF(pdfDataUrl, pdfPreview) {
    const iframe = document.createElement('iframe');
    iframe.src = pdfDataUrl;
    iframe.classList.add('pdf-iframe');
    iframe.setAttribute('title', 'PDF Preview');  // Accessibility
    pdfPreview.appendChild(iframe);
}
