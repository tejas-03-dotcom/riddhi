from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageDraw
import pytesseract
from textblob import TextBlob
import os
import io

app = Flask(__name__)

# Set path to Tesseract if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def enhance_image(img):
    img = img.convert("RGBA")
    img = ImageEnhance.Brightness(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    return img


def is_misspelled(word):
    if word.isdigit() or len(word) < 2:
        return False
    corrected = TextBlob(word).correct()
    return corrected.lower() != word.lower()


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    misspelled_count = 0

    if request.method == 'POST':
        image_file = request.files['image']
        if image_file:
            img = Image.open(image_file.stream)
            img = enhance_image(img)

            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            for i, word in enumerate(data['text']):
                if word.strip() and data['conf'][i] != '-1' and int(data['conf'][i]) > 60:
                    if is_misspelled(word):
                        misspelled_count += 1
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 0, 100))
                    text += word + " "

            result_img = Image.alpha_composite(img, overlay).convert("RGB")
            result_img.save('static/output.png')

    return render_template("index.html", text=text, misspelled=misspelled_count)


@app.route('/download')
def download():
    return send_file("static/output.png", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
