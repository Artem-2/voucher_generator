import qrcode
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from barcode import Code128

def make_white_background_transparent(img_path):
    img = Image.open(img_path)
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == (255, 255, 255):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    img.save(img_path)



def create_qr_code(data, file_path, zoom = {"coefficient": 1}):
    file_path += ".png"
    qr = qrcode.QRCode(version=1, box_size=10 * zoom["coefficient"], border=0)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    if zoom["coefficient"] != 1:
        qr_img = qr_img.resize((int(zoom["Width"]), int(zoom["Height"])), Image.Resampling.LANCZOS)
    qr_img.save("png\\" + file_path)
    make_white_background_transparent("png\\" + file_path)


def create_bar_code(data, file_path, width = 1, height = 0.5):
    options = {
        'write_text': False,  # Отключаем текст снизу
        'quiet_zone': 0,  # Задаем размер зоны вокруг штрих-кода
        'module_width': width,  # Задаем ширину модуля
        'module_height': 10 * height + 20,  # Задаем высоту модуля
    }
    barcode = Code128(data, writer=ImageWriter())
    barcode.save("png\\" + file_path, options=options)
    file_path += ".png"
    make_white_background_transparent("png\\" + file_path)



def create_text(data, file_path, zoom = {"coefficient": 1}):
    file_path += ".png"
    font = ImageFont.truetype(data["font_path"], int(12*zoom["coefficient"]))
    temp_img = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), data["text"], font=font)
    width, height = bbox[2], bbox[3]
    text_img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_img)
    draw.text((0, 0), data["text"], font=font, fill=(0, 0, 0))
    Width, Height = text_img.size
    if zoom["coefficient"] != 1:
        text_img = text_img.resize((int(Width), int(zoom["Height"])), Image.Resampling.LANCZOS)
    text_img.save("png\\" + file_path)

