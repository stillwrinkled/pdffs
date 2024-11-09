function setupDragDrop() {
    const dragDropZones = document.querySelectorAll('.drag-drop-zone');

    dragDropZones.forEach(zone => {
        const fileInput = zone.querySelector('input[type="file"]');

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
                handleFiles(e.dataTransfer.files, fileInput, zone.querySelector('.file-list'));
            }
        });

        zone.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files, fileInput, zone.querySelector('.file-list'));
        });
    });
}

function handleFiles(files, fileInput, fileList) {
    const dataTransfer = new DataTransfer();

    // Add existing files
    for (let i = 0; i < fileInput.files.length; i++) {
        dataTransfer.items.add(fileInput.files[i]);
    }

    // Add new files
    for (let i = 0; i < files.length; i++) {
        dataTransfer.items.add(files[i]);
    }

    fileInput.files = dataTransfer.files;

    // Update file list display
    fileList.innerHTML = '';
    for (let i = 0; i < fileInput.files.length; i++) {
        const li = document.createElement('li');
        li.textContent = fileInput.files[i].name;
        fileList.appendChild(li);
    }
}

document.addEventListener('DOMContentLoaded', setupDragDrop);
