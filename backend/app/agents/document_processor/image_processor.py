 from PIL import Image

def preprocess_image(image_path: str):
    """
    Preprocesses an image for better OCR results.
    """
    try:
        img = Image.open(image_path)
        # Placeholder for image preprocessing steps like deskew, denoise, etc.
        return img
    except Exception as e:
        print(f"Error processing image file: {e}")
        return None
