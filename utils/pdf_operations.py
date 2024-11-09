import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pytesseract
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image
import zipfile
import os
import subprocess
from fpdf import FPDF
from flask import send_file
from io import BytesIO
from xhtml2pdf import pisa
import pdfkit
from flask import flash
import tempfile
from pdf2image import convert_from_bytes
from pytesseract import image_to_string
from docx import Document
from openpyxl import Workbook
import io
from PyPDF2 import PdfReader, PdfWriter
from flask import send_file


def merge_pdfs(files):
    merger = PyPDF2.PdfMerger()
    for file in files:
        merger.append(file)
    output = io.BytesIO()
    merger.write(output)
    output.seek(0)
    return output


def split_pdf(file, split_option, page_range=None, x_pages=None):
    reader = PyPDF2.PdfReader(file)
    total_pages = len(reader.pages)
    outputs = []

    if split_option == 'range':
        # Extract specific page range (start and end)
        start_page, end_page = map(int, page_range.split('-'))
        start_page -= 1  # Pages are 0-indexed
        writer = PyPDF2.PdfWriter()
        for page in range(start_page, end_page):
            writer.add_page(reader.pages[page])

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        outputs.append(output)

    elif split_option == 'every-x-pages':
        # Split every X pages
        x_pages = int(x_pages)
        for i in range(0, total_pages, x_pages):
            writer = PyPDF2.PdfWriter()
            for j in range(i, min(i + x_pages, total_pages)):
                writer.add_page(reader.pages[j])

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            outputs.append(output)

    return outputs


# Utility to run Ghostscript for high-level compression
def run_ghostscript(input_pdf, output_pdf, compression_level):
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS={compression_level}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]
    subprocess.run(gs_command, check=True)


def compress_pdf(file, compression_level='1/4'):
    # Check if the file is a valid PDF
    if not file.filename.endswith('.pdf'):
        raise ValueError("Invalid file type. Please upload a PDF file.")

    # Ensure we're reading from the start of the file
    file.seek(0)
    pdf_data = file.read()

    # Create temporary file paths for input and output
    temp_input = 'temp_input.pdf'
    temp_output = 'temp_output.pdf'

    # Write the uploaded PDF to the temporary input file
    with open(temp_input, 'wb') as f:
        f.write(pdf_data)

    # Choose the compression level based on the user selection
    if compression_level == '1/4':
        compression_type = '/screen'  # Max compression
    elif compression_level == '1/2':
        compression_type = '/ebook'  # Medium compression
    elif compression_level == '1/3':
        compression_type = '/printer'  # Moderate compression
    elif compression_level == '1/10':
        compression_type = '/prepress'  # Least compression
    else:
        compression_type = '/default'  # Default compression

    # Run Ghostscript to compress the file
    run_ghostscript(temp_input, temp_output, compression_type)

    # Read the compressed file and return it as bytes
    output_pdf = io.BytesIO()
    with open(temp_output, 'rb') as f:
        output_pdf.write(f.read())

    # Clean up temporary files
    os.remove(temp_input)
    os.remove(temp_output)

    output_pdf.seek(0)
    return output_pdf


# Existing functions remain unchanged, for example:
def merge_pdfs(files):
    merger = PyPDF2.PdfMerger()
    for file in files:
        merger.append(file)
    output = io.BytesIO()
    merger.write(output)
    output.seek(0)
    return output


"""
def add_watermark(file, watermark_text):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    # A4 page size in points: 595x842
    a4_width, a4_height = 595, 842

    watermark_stream = io.BytesIO()
    c = canvas.Canvas(watermark_stream, pagesize=(a4_width, a4_height))

    # Set font and color for watermark
    c.setFont("Helvetica", 60)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.3)

    # Save the state and translate to the center of the page
    c.saveState()
    c.translate(a4_width / 2, a4_height / 2)  # Center of the page
    c.rotate(45)  # Rotate diagonally

    # Draw the watermark text in the center
    c.drawCentredString(0, 0, watermark_text)

    # Restore state and finalize the canvas
    c.restoreState()
    c.save()

    watermark_stream.seek(0)
    watermark = PyPDF2.PdfReader(watermark_stream)

    # Apply watermark to each page
    for page in reader.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    # Output the watermarked PDF
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output 
    """


def add_watermark(file, watermark_text):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    # Create the watermark text as a template in a separate canvas
    watermark_stream = io.BytesIO()
    watermark_template = canvas.Canvas(watermark_stream)

    # Set the font and watermark properties
    watermark_template.setFont("Helvetica", 60)
    watermark_template.setFillColorRGB(0.5, 0.5, 0.5, 0.3)

    # For each page in the PDF
    for page_num, page in enumerate(reader.pages):
        # Get the dimensions of the current page
        page_width = page.mediabox.upper_right[0]
        page_height = page.mediabox.upper_right[1]

        # Reset the canvas with the current page size
        watermark_template.setPageSize((page_width, page_height))

        # Translate to the center of the page and rotate diagonally
        watermark_template.saveState()
        watermark_template.translate(page_width / 2, page_height / 2)
        watermark_template.rotate(45)

        # Draw the watermark centered on the page
        watermark_template.drawCentredString(0, 0, watermark_text)
        watermark_template.restoreState()

        # Finish the page
        watermark_template.showPage()

    # Finalize the watermark template
    watermark_template.save()
    watermark_stream.seek(0)
    watermark_pdf = PyPDF2.PdfReader(watermark_stream)

    # Merge the watermark onto each page
    for page_num, page in enumerate(reader.pages):
        page.merge_page(watermark_pdf.pages[0])
        writer.add_page(page)

    # Output the watermarked PDF
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def add_page_numbers(file):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    for i, page in enumerate(reader.pages):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(550, 25, str(i + 1))
        c.save()
        packet.seek(0)
        number = PyPDF2.PdfReader(packet)
        page.merge_page(number.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def rotate_pdf(file, angle):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def delete_pages(file, pages_to_delete):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    pages_to_delete = [int(p) for p in pages_to_delete.replace(' ', '').split(',')]
    for i, page in enumerate(reader.pages):
        if i + 1 not in pages_to_delete:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def fill_form(file, form_data):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    writer.append(reader)
    writer.update_page_form_field_values(writer.pages[0], form_data)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def perform_ocr(file):
    pdf_bytes = file.read()
    images = convert_from_bytes(pdf_bytes)

    ocr_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        ocr_text += text + "\n\n"

    return ocr_text


def zip_files(files):
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, file_data in enumerate(files):
            zf.writestr(f'split_part_{idx + 1}.pdf', file_data.getvalue())
    zip_stream.seek(0)
    return zip_stream


# New function for HTML to PDF conversion
def html_to_pdf(html_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Split the HTML content into lines and add them to the PDF
    for line in html_content.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)

    # Save the PDF to a BytesIO object for sending as a file response
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output


def url_to_pdf(url):
    import tempfile
    import os
    from flask import flash

    # Configure pdfkit to use wkhtmltopdf with landscape orientation
    options = {
        'enable-local-file-access': None,
        'quiet': '',
        'orientation': 'Landscape',  # Set PDF to landscape orientation
        'no-stop-slow-scripts': None,  # Avoid stopping due to slow scripts
        'disable-javascript': None  # Disable JavaScript if not needed for rendering
    }

    # Disclaimer about conversion time
    disclaimer = "Note: Conversion time may vary due to page complexity and external resources."
    flash(disclaimer)

    try:
        # Create a temporary file to store the PDF output
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            pdfkit.from_url(url, temp_pdf.name, options=options)

            output = BytesIO()
            with open(temp_pdf.name, 'rb') as f:
                output.write(f.read())

            output.seek(0)
        return output

    except OSError as e:
        flash("Error generating PDF. Please check if the URL is accessible and try again.", "error")
        raise ValueError(f"Failed to convert URL to PDF: {e}")


def compress_pdf(input_pdf_path, output_pdf_path, compression_ratio):
    """Helper function to compress a PDF file."""
    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dNOPAUSE",
        "-dBATCH",
        "-sOutputFile=" + output_pdf_path,
        input_pdf_path
    ]
    if compression_ratio == 0.6:
        # Apply stronger compression
        gs_command.extend(["-dPDFSETTINGS=/screen", "-dColorImageResolution=100"])
    elif compression_ratio == 0.3:
        # Apply moderate compression
        gs_command.append("-dPDFSETTINGS=/ebook")

    subprocess.run(gs_command, check=True)


import tempfile
import os
from pdf2image import convert_from_bytes
from pytesseract import image_to_string
from docx import Document
from openpyxl import Workbook
import io


def ocr_pdf_to_docx_or_xlsx(file):
    # Reject files that look like presentations based on filename or content type
    if "PPT" in file.filename or "Slide" in file.filename:
        raise ValueError("This format is not supported for OCR. Please upload a document-based PDF.")

    try:
        # Convert PDF to images for OCR processing
        images = convert_from_bytes(file.read())
        text_data = ""

        # Prepare output files
        doc_output = io.BytesIO()
        xlsx_output = io.BytesIO()

        doc = Document()
        wb = Workbook()
        ws = wb.active

        is_table_like = False  # To determine if content is table-like for XLSX

        for page_num, image in enumerate(images):
            # Extract text using OCR
            page_text = image_to_string(image)
            text_data += page_text

            # Add text to DOCX
            doc.add_paragraph(page_text)

            # Check if the text has table-like rows and columns
            for line in page_text.splitlines():
                # Simple heuristic: if multiple tabs or spaces between words, consider it table-like
                if '\t' in line or line.count('  ') > 1:
                    is_table_like = True
                ws.append([line])  # Add each line as a row in XLSX

        # Determine output based on content structure
        if is_table_like:
            # Save as XLSX if table-like structures are detected
            wb.save(xlsx_output)
            xlsx_output.seek(0)
            output_filename = "converted_file.xlsx"
            return xlsx_output, output_filename
        else:
            # Save as DOCX otherwise
            doc.save(doc_output)
            doc_output.seek(0)
            output_filename = "converted_file.docx"
            return doc_output, output_filename

    except Exception as e:
        raise ValueError(f"OCR failed: {e}")


import io
from PyPDF2 import PdfReader, PdfWriter


def fill_pdf_form(file, form_data):
    reader = PdfReader(file)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages):
        writer.add_page(page)
        for field_name, field_value in form_data.items():
            if field_name in page.get_fields():
                page.update_field(field_name, field_value)

    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf


def save_filled_form(file, form_data):
    """
    This function opens a PDF form, fills it with the provided data, and returns it as a BytesIO object.

    Args:
    - file: Path to the PDF form file.
    - form_data: A dictionary containing form field names and their respective values.

    Returns:
    - BytesIO object of the filled PDF.
    """
    # Open the original form, fill it, and save the result in memory
    with open(file, 'rb') as pdf_file:
        filled_pdf = fill_pdf_form(pdf_file, form_data)

    return filled_pdf
