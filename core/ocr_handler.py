import easyocr
from PIL import Image, ImageEnhance
import numpy as np

class OCRHandler:
    def __init__(self):
        self.reader = easyocr.Reader(['en']) # TODO: Add support for multiple languages

    def process_image(self, image_path):
        image = Image.open(image_path)
        image = ImageEnhance.Contrast(image).enhance(2.0)
        results = self.reader.readtext(np.array(image))
        return results