from flask import Flask, render_template, request, send_file
import os
from utils import pdf_operations, file_conversions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['GET', 'POST'])
def merge():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if files:
            merged_file = pdf_operations.merge_pdfs(files)
            return send_file(merged_file, as_attachment=True, download_name='merged.pdf')
    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
def split():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            split_files = pdf_operations.split_pdf(file)
            # Implementation for sending multiple files as a zip
            return "Split successful"
    return render_template('split.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            compressed_file = pdf_operations.compress_pdf(file)
            return send_file(compressed_file, as_attachment=True, download_name='compressed.pdf')
    return render_template('compress.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        file = request.files['file']
        format = request.form['format']
        if file and format:
            converted_file = file_conversions.convert_pdf(file, format)
            return send_file(converted_file, as_attachment=True, download_name=f'converted.{format}')
    return render_template('convert.html')

@app.route('/watermark', methods=['GET', 'POST'])
def watermark():
    if request.method == 'POST':
        file = request.files['file']
        watermark_text = request.form['watermark_text']
        if file and watermark_text:
            watermarked_file = pdf_operations.add_watermark(file, watermark_text)
            return send_file(watermarked_file, as_attachment=True, download_name='watermarked.pdf')
    return render_template('watermark.html')

@app.route('/page_numbers', methods=['GET', 'POST'])
def page_numbers():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            numbered_file = pdf_operations.add_page_numbers(file)
            return send_file(numbered_file, as_attachment=True, download_name='numbered.pdf')
    return render_template('page_numbers.html')

@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        file = request.files['file']
        angle = int(request.form['angle'])
        if file and angle:
            rotated_file = pdf_operations.rotate_pdf(file, angle)
            return send_file(rotated_file, as_attachment=True, download_name='rotated.pdf')
    return render_template('rotate.html')

@app.route('/delete_pages', methods=['GET', 'POST'])
def delete_pages():
    if request.method == 'POST':
        file = request.files['file']
        pages_to_delete = request.form['pages_to_delete']
        if file and pages_to_delete:
            modified_file = pdf_operations.delete_pages(file, pages_to_delete)
            return send_file(modified_file, as_attachment=True, download_name='modified.pdf')
    return render_template('delete_pages.html')

@app.route('/html_to_pdf', methods=['GET', 'POST'])
def html_to_pdf():
    if request.method == 'POST':
        html_content = request.form['html_content']
        if html_content:
            pdf_file = file_conversions.html_to_pdf(html_content)
            return send_file(pdf_file, as_attachment=True, download_name='converted.pdf')
    return render_template('html_to_pdf.html')

@app.route('/form_fill', methods=['GET', 'POST'])
def form_fill():
    if request.method == 'POST':
        file = request.files['file']
        form_data = request.form.to_dict()
        if file and form_data:
            filled_file = pdf_operations.fill_form(file, form_data)
            return send_file(filled_file, as_attachment=True, download_name='filled_form.pdf')
    return render_template('form_fill.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
