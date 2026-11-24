import os
from PIL import Image
from app.config.settings import settings
from app.utils.logger import logger

def extract_text_with_ocr(image_path_or_pil) -> str:
    """Extracts text from image using pytesseract with fallback guards."""
    try:
        import pytesseract
        
        if settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

        if isinstance(image_path_or_pil, str):
            image = Image.open(image_path_or_pil)
        else:
            image = image_path_or_pil

        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR extraction unavailable or Tesseract not found ({e}). Returning fallback status.")
        return "[OCR extraction fallback: Tesseract executable not detected on environment PATH]"
