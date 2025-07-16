import pytesseract
from PIL import Image
import io

# ✅ Set path to tesseract.exe for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_file):
    image = Image.open(io.BytesIO(image_file.read()))
    return pytesseract.image_to_string(image)
