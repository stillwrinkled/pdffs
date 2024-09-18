import io
from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from xhtml2pdf import pisa
from PyPDF2 import PdfReader

def convert_pdf(file, format):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    output = io.BytesIO()

    if format == 'docx':
        doc = Document()
        doc.add_paragraph(text)
        doc.save(output)
    elif format == 'xlsx':
        wb = Workbook()
        ws = wb.active
        for i, line in enumerate(text.split('\n'), 1):
            ws.cell(row=i, column=1, value=line)
        wb.save(output)
    elif format == 'pptx':
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        text_box = slide.shapes.add_textbox(10, 10, 600, 400)
        text_frame = text_box.text_frame
        text_frame.text = text
        prs.save(output)

    output.seek(0)
    return output

def html_to_pdf(html_content):
    output = io.BytesIO()
    pisa.CreatePDF(html_content, dest=output)
    output.seek(0)
    return output
