import os
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import barcode
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile

class PDFModifier:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.coordinates = []

    def add_elements(self, barcode_text, qr_text, texts):
        reader = PdfReader(self.pdf_path)
        writer = PdfWriter()
        
        for page_number in range(len(reader.pages)):
            packet = BytesIO()
            
            can = canvas.Canvas(packet, pagesize=letter)
            page_data = reader.pages[page_number]
            can.setPageSize((page_data.mediabox.width, page_data.mediabox.height))
            
            # Добавляем штрих-код
            barcode_img = self.create_barcode(barcode_text)
            self.place_image_on_pdf(can, barcode_img, 50, 100)

            # Добавляем QR-код
            qr_img = self.create_qr_code(qr_text)
            self.place_image_on_pdf(can, qr_img, 50, 500)

            # Добавляем текст
            self.add_text(can, texts)

            can.save()

            packet.seek(0)
            new_pdf = PdfReader(packet)
            page = reader.pages[page_number]
            page.merge_page(new_pdf.pages[0])

            writer.add_page(page)

        with open("output.pdf", "wb") as file:
            writer.write(file)
        
        return self.coordinates

    def create_barcode(self, text):
        barcode_cls = get_barcode_class('code128')
        barcode_data = barcode_cls(text, writer=ImageWriter())

        img_fp = BytesIO()
        barcode_data.write(img_fp, options={"write_text": False})
        img_fp.seek(0)

        img = Image.open(img_fp)

        # Переводим изображение в градации серого
        gray_img = img.convert('L')

        # Получаем данные пикселей
        pixel_data = gray_img.load()

        # Избавляемся от белой обводки путем поиска границ штрих-кода
        width, height = gray_img.size

        def find_borders(pixel_data, width, height):
                top, bottom, left, right = None, None, None, None

                # Найти верхнюю границу
                for y in range(height):
                        for x in range(width):
                                if pixel_data[x, y] < 255: # не белый пиксель
                                        top = y
                                        break
                        if top is not None:
                                break

                # Найти нижнюю границу
                for y in range(height - 1, -1, -1):
                        for x in range(width):
                                if pixel_data[x, y] < 255: # не белый пиксель
                                        bottom = y
                                        break
                        if bottom is not None:
                                break

                # Найти левую границу
                for x in range(width):
                        for y in range(height):
                                if pixel_data[x, y] < 255: # не белый пиксель
                                        left = x
                                        break
                        if left is not None:
                                break

                # Найти правую границу
                for x in range(width - 1, -1, -1):
                        for y in range(height):
                                if pixel_data[x, y] < 255: # не белый пиксель
                                        right = x
                                        break
                        if right is not None:
                                break

                return left, top, right, bottom

        left, top, right, bottom = find_borders(pixel_data, width, height)

        # Обрезаем изображение до контента
        img = img.crop((left, top, right + 1, bottom + 1))

        return img



    def create_qr_code(self, data):
        qr = qrcode.QRCode(border=0)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        datas = qr_img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0)) # прозрачный
            else:
                new_data.append(item)
        qr_img.putdata(new_data)

        return qr_img

    def place_image_on_pdf(self, canvas, img, x, y):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                img.save(tmp_file, format='PNG')
                tmp_file_path = tmp_file.name

        # Получить размеры изображения
        img_width, img_height = img.size

        # Нарисовать изображение на PDF
        canvas.drawImage(tmp_file_path, x, y, width=img_width, height=img_height)

        # Теперь добавляем рамку вокруг изображения
        canvas.setStrokeColorRGB(1, 0, 0) # Пример: красная рамка
        # Использовать img_width и img_height для точного соответствия обводке
        canvas.rect(x, y, img_width, img_height, stroke=1)

        self.coordinates.append((x, y, img_width, img_height))
        os.unlink(tmp_file_path)

    def add_text(self, canvas, texts):
        x, y = 300, 700
        fonts = ["arial.ttf", "times.ttf"] # Путевые пути для шрифтов

        for i, (text, font_path) in enumerate(zip(texts, fonts)):
            pdfmetrics.registerFont(TTFont(font_path.split('.ttf')[0], font_path))
            canvas.setFont(font_path.split('.ttf')[0], 14)

            text_lines = simpleSplit(text, canvas._fontname, canvas._fontsize, canvas._pagesize[0])
            max_text_width = max(canvas.stringWidth(line, font_path.split('.ttf')[0], 14) for line in text_lines)
            text_height = 14 * len(text_lines)

            text_y = y - i * 50 + 20 # Сдвигаем текст вверх на 20 единиц
            canvas.drawString(x, text_y, text)

            # Добавляем рамку вокруг текста
            canvas.setStrokeColorRGB(0, 1, 0) # Пример: зеленая рамка
            canvas.rect(x, text_y - text_height, max_text_width, text_height, stroke=1)

            self.coordinates.append((x, text_y - text_height, max_text_width, text_height))

# Пример использования
pdf_modifier = PDFModifier('input_pdf\\input.pdf')
elements_coordinates = pdf_modifier.add_elements("barcode1231231213", "This is a QR Code", ["First text", "Second text"])
print("Elements coordinates:", elements_coordinates)
