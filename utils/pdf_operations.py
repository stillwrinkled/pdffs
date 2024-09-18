import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def merge_pdfs(files):
    merger = PyPDF2.PdfMerger()
    for file in files:
        merger.append(file)
    output = io.BytesIO()
    merger.write(output)
    output.seek(0)
    return output

def split_pdf(file):
    reader = PyPDF2.PdfReader(file)
    outputs = []
    for i in range(len(reader.pages)):
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[i])
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        outputs.append(output)
    return outputs

def compress_pdf(file):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def add_watermark(file, watermark_text):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()

    # Create watermark
    watermark_stream = io.BytesIO()
    c = canvas.Canvas(watermark_stream, pagesize=letter)
    c.setFont("Helvetica", 60)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.3)
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, watermark_text)
    c.restoreState()
    c.save()
    watermark_stream.seek(0)
    watermark = PyPDF2.PdfReader(watermark_stream)

    for page in reader.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

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
