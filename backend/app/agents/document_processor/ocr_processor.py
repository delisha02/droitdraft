import pytesseract
from PIL import Image
from app.agents.document_processor.image_processor import preprocess_image

def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text from an image file using OCR (Tesseract).
    
    Requires Tesseract to be installed on the system.
    """
    try:
        # Preprocess the image for better OCR results
        img = preprocess_image(file_path)
        if img:
            # Perform OCR
            text = pytesseract.image_to_string(img)
            return text
        return ""
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return ""
