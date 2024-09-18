document.addEventListener('DOMContentLoaded', () => {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const fileName = e.target.files[0].name;
            const label = input.nextElementSibling;
            label.textContent = fileName;
        });
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a file before submitting.');
            }
        });
    });
});

function previewPDF(input) {
    const file = input.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const pdfPreview = document.getElementById('pdf-preview');
        pdfPreview.src = e.target.result;
        pdfPreview.style.display = 'block';
    }

    reader.readAsDataURL(file);
}
