from flask import Flask, render_template, request, send_file
import os
from utils import pdf_operations, file_conversions  # Ensure this line is correct
from flask import send_file

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
        split_option = request.form['split_option']
        page_range = request.form.get('page_range')  # Only relevant if splitting by range
        x_pages = request.form.get('x_pages')  # Only relevant if splitting every X pages

        if file:
            if split_option == 'range' and page_range:
                split_files = pdf_operations.split_pdf(file, split_option, page_range=page_range)
            elif split_option == 'every-x-pages' and x_pages:
                split_files = pdf_operations.split_pdf(file, split_option, x_pages=x_pages)
            else:
                return "Invalid input", 400

            if len(split_files) == 1:
                return send_file(split_files[0], as_attachment=True, download_name='split_output.pdf')
            else:
                zip_output = pdf_operations.zip_files(split_files)
                return send_file(zip_output, as_attachment=True, download_name='split_files.zip')
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
            try:
                converted_file, filename = file_conversions.convert_pdf(file, format)
                if filename.endswith('.zip'):
                    return send_file(converted_file, as_attachment=True, download_name=filename,
                                     mimetype='application/zip')
                else:
                    return send_file(converted_file, as_attachment=True, download_name=filename,
                                     mimetype=f'image/{format}')
            except ValueError as e:
                # Return error to frontend if conversion fails
                return render_template('convert.html', error=str(e))
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


@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    format = request.form.get('format')

    converted_file, filename = file_conversions.convert_pdf(file, format)

    # Send the file using Flask's send_file
    return send_file(
        converted_file,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
