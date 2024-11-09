from flask import Flask, render_template, request, send_file, flash, get_flashed_messages, redirect, url_for
import os
from utils import pdf_operations, file_conversions
from utils.pdf_operations import ocr_pdf_to_docx_or_xlsx

from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from utils.pdf_operations import fill_pdf_form, save_filled_form  # Import your utility functions
import os
import io
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = "your_secret_key"

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/merge', methods=['GET', 'POST'])
def merge():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        files = request.files.getlist('files')
        if files:
            merged_file = pdf_operations.merge_pdfs(files)
            return send_file(merged_file, as_attachment=True, download_name='merged.pdf')
    return render_template('merge.html')


@app.route('/split', methods=['GET', 'POST'])
def split():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        split_option = request.form['split_option']
        page_range = request.form.get('page_range')
        x_pages = request.form.get('x_pages')

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
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        if file:
            compressed_file = pdf_operations.compress_pdf(file)
            return send_file(compressed_file, as_attachment=True, download_name='compressed.pdf')
    return render_template('compress.html')


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    get_flashed_messages()  # Clear existing messages
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
                                     mimetype=f'application/{format}')
            except ValueError as e:
                flash(f"Conversion error: {str(e)}", "error")
    return render_template('convert.html')


@app.route('/watermark', methods=['GET', 'POST'])
def watermark():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        watermark_text = request.form['watermark_text']
        if file and watermark_text:
            watermarked_file = pdf_operations.add_watermark(file, watermark_text)
            return send_file(watermarked_file, as_attachment=True, download_name='watermarked.pdf')
    return render_template('watermark.html')


@app.route('/page_numbers', methods=['GET', 'POST'])
def page_numbers():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        if file:
            numbered_file = pdf_operations.add_page_numbers(file)
            return send_file(numbered_file, as_attachment=True, download_name='numbered.pdf')
    return render_template('page_numbers.html')


@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        angle = int(request.form['angle'])
        if file and angle:
            rotated_file = pdf_operations.rotate_pdf(file, angle)
            return send_file(rotated_file, as_attachment=True, download_name='rotated.pdf')
    return render_template('rotate.html')


@app.route('/delete_pages', methods=['GET', 'POST'])
def delete_pages():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        pages_to_delete = request.form['pages_to_delete']
        if file and pages_to_delete:
            modified_file = pdf_operations.delete_pages(file, pages_to_delete)
            return send_file(modified_file, as_attachment=True, download_name='modified.pdf')
    return render_template('delete_pages.html')


@app.route('/url_to_pdf', methods=['GET', 'POST'])
def url_to_pdf():
    # Clear flashed messages to avoid duplications or leftovers
    get_flashed_messages()

    if request.method == 'GET':
        # Flash only the disclaimer on initial page load
        flash("Note: Conversion time may vary due to page complexity and external resources.", "info")
        return render_template('url_to_pdf.html')

    elif request.method == 'POST':
        url = request.form['url']
        try:
            # Attempt URL conversion to PDF
            pdf_file = pdf_operations.url_to_pdf(url)
            pdf_size_mb = len(pdf_file.getvalue()) / (1024 * 1024)

            # Apply compression if necessary
            if pdf_size_mb > 10:
                compression_level = '1/10' if pdf_size_mb > 27 else '1/3'
                pdf_file = pdf_operations.compress_pdf(pdf_file, compression_level=compression_level)
                flash("Processing large file sizes may increase conversion time. Compressed for faster download.",
                      "info")

            # Send the file as a response
            return send_file(pdf_file, as_attachment=True, download_name='url_converted.pdf')

        except (ValueError, OSError) as e:
            # Flash error message only for conversion issues, without re-flashing disclaimer
            if 'network error' in str(e).lower():
                flash("Error generating PDF. Please check if the URL is accessible and try again.", "error")
            else:
                flash("Could not access the webpage or process the URL. Please check the URL or try a different one.",
                      "error")
            return render_template('url_to_pdf.html')


@app.route('/ocr_pdf', methods=['GET', 'POST'])
def ocr_pdf():
    get_flashed_messages()  # Clear existing messages
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                app.logger.info(f"Received file for OCR: {file.filename}")
                output_file, output_filename = ocr_pdf_to_docx_or_xlsx(file)
                app.logger.info(f"OCR processing successful, sending file: {output_filename}")
                return send_file(output_file, as_attachment=True, download_name=output_filename)
            except ValueError as e:
                app.logger.error(f"OCR processing error: {e}")
                flash(str(e), "error")
    return render_template('ocr_pdf.html')


@app.route('/form_fill', methods=['GET', 'POST'])
def form_fill():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file uploaded.", "error")
            logging.error("No file uploaded.")
            return render_template('form_fill.html')

        # Check if file has a PDF extension
        if not file.filename.endswith('.pdf'):
            flash("Invalid file type. Please upload a PDF file.", "error")
            logging.error("Invalid file type: %s", file.filename)
            return render_template('form_fill.html')

        # Secure and save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            logging.info("File saved successfully: %s", file_path)
            return redirect(url_for('form_fill_view', filename=filename))
        except Exception as e:
            logging.exception("Failed to save file: %s", str(e))
            flash("An error occurred while uploading the file.", "error")
            return render_template('form_fill.html')

    # Render upload form
    return render_template('form_fill.html')


@app.route('/form_fill/view/<filename>', methods=['GET', 'POST'])
def form_fill_view(filename):
    if request.method == 'POST':
        # Log and process form data
        filled_data = request.form.to_dict()
        logging.info("Form data received: %s", filled_data)

        # Attempt to save filled form
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            filled_pdf = save_filled_form(file_path, filled_data)
            filled_pdf.seek(0)
            logging.info("Filled PDF generated successfully.")
            return send_file(filled_pdf, as_attachment=True, download_name=f"filled_{filename}")
        except Exception as e:
            logging.exception("Failed to generate filled PDF: %s", str(e))
            flash("An error occurred while generating the filled PDF.", "error")
            return redirect(url_for('form_fill_view', filename=filename))

    # Render the fill form preview
    try:
        logging.info("Rendering form fill preview for file: %s", filename)
        return render_template('fill_form_view.html', filename=filename)
    except Exception as e:
        logging.exception("Error rendering form fill view: %s", str(e))
        flash("An error occurred while loading the form preview.", "error")
        return redirect(url_for('form_fill'))


@app.route('/form_fill/save/<filename>', methods=['POST'])
def save_filled_form_route(filename):
    filled_data = request.form.to_dict()  # Collect filled data
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        filled_pdf = save_filled_form(file_path, filled_data)  # Call save_filled_form function
        filled_pdf.seek(0)
        logging.info("Filled form saved and ready for download: %s", filename)
        return send_file(filled_pdf, as_attachment=True, download_name=f"filled_{filename}")
    except Exception as e:
        logging.exception("Failed to save and send filled PDF: %s", str(e))
        flash("An error occurred while saving the filled form.", "error")
        return redirect(url_for('form_fill_view', filename=filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
