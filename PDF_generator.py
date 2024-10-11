from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.graphics.barcode import qr, code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF # Import renderPDF
from PIL import Image, ImageOps
from io import BytesIO
import os
    

class PDFModifier:
    def __init__(self, input_pdf_path):
        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = "modified_output.pdf"
    
    def add_elements_to_pdf(self, text_data, qr_data, barcode_data, font_paths, positions):
        # Read the existing PDF
        reader = PdfReader(self.input_pdf_path)
        writer = PdfWriter()
        
        # Create a temporary PDF with reportlab
        buffer = BytesIO()
        packet = canvas.Canvas(buffer, pagesize=A4)
        
        # Add Texts
        for i, (text, font_path, position, font_size) in enumerate(zip(text_data, font_paths, positions["text"], positions["text_size"])):
            packet.setFont(self._add_font_to_canvas(packet, font_path, f"CustomFont{i}"), font_size)
            packet.drawString(position[0], position[1], text)
        
        # Add QR Code
        for qr_string, position, size in zip(qr_data, positions["qr"], positions["qr_size"]):
            qr_code = qr.QrCodeWidget(qr_string)
            bounds = qr_code.getBounds()
            w = bounds[2] - bounds[0]
            h = bounds[3] - bounds[1]
            barcode_image = self._barcode_to_image(qr_code, w, h, size)
            img = ImageReader(barcode_image)
            packet.drawImage(img, position[0], position[1], mask='auto')

        # Add Barcode
        for barcode_string, position, size in zip(barcode_data, positions["barcode"], positions["barcode_size"]):
            barcode = code128.Code128(barcode_string)
            bounds = barcode.getBounds()
            w = bounds[2] - bounds[0]
            h = bounds[3] - bounds[1]
            barcode_image = self._barcode_to_image(barcode, w, h, size)
            img = ImageReader(barcode_image)
            packet.drawImage(img, position[0], position[1], mask='auto')

        packet.save()
        
        # Merge temporary PDF with original
        buffer.seek(0)
        new_pdf = PdfReader(buffer)
        
        for page in reader.pages:
            writer.add_page(page)
        
        for page in new_pdf.pages:
            writer.pages[0].merge_page(page)
        
        # Write the final output PDF
        with open(self.output_pdf_path, 'wb') as out_pdf:
            writer.write(out_pdf)

    def _add_font_to_canvas(self, packet, font_path, font_name):
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name

    def _barcode_to_image(self, barcode, w, h, size):
        ''' Create barcode image without white borders '''
        barcode_image_buffer = BytesIO()
        barcode_draw = Drawing(size[0], size[1])
        barcode_black = barcode
        barcode_black.barFillColor = colors.black
        barcode_black.barStrokeColor = colors.black
        barcode_draw.add(barcode_black)

        # Render to the buffer
        renderPDF.drawToFile(barcode_draw, barcode_image_buffer)

        # Set buffer position to start
        barcode_image_buffer.seek(0)

        # Attempt to convert directly to an image if format permits
        try:
            barcode_image = Image.open(barcode_image_buffer)
            barcode_image = ImageOps.invert(barcode_image.convert('L'))
            barcode_image = barcode_image.convert("RGBA")
        except Exception as e:
            print(f"Error opening image from buffer: {e}")
            # Optionally save for debugging
            with open('debug_image_output.pdf', 'wb') as f:
                f.write(barcode_image_buffer.getvalue())
            raise

        barcode_image_buffer.close()
        return barcode_image


# Пример использования

text_data = ["Пример текста 1", "Пример текста 2"]
qr_data = ["https://example.com/qrcode1", "https://example.com/qrcode2"]
barcode_data = ["123456789012", "987654321098"]
font_paths = ["arial.ttf", "tahoma.ttf"]
positions = {
    "text": [(100, 200), (100, 300)],
    "qr": [(200, 400), (200, 500)],
    "barcode": [(300, 600), (300, 700)],
    "text_size": [12, 14],
    "qr_size": [(100, 100), (120, 120)],
    "barcode_size": [(150, 50), (150, 50)],
}

modifier = PDFModifier("original.pdf")
modifier.add_elements_to_pdf(text_data, qr_data, barcode_data, font_paths, positions)
