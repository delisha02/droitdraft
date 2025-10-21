import os
from app.agents.document_processor.docx_processor import extract_text_from_docx
from app.agents.document_processor.pdf_processor import extract_text_from_pdf
from app.agents.document_processor.ocr_processor import extract_text_from_image

def extract_text(file_path: str) -> str:
    """
    Extracts text from a file, automatically detecting the file type.
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == ".docx":
        return extract_text_from_docx(file_path)
    elif file_extension == ".pdf":
        # This will only extract text from text-based PDFs.
        # For image-based PDFs, a more advanced solution involving OCR is needed.
        return extract_text_from_pdf(file_path)
    elif file_extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"]:
        return extract_text_from_image(file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
        return ""
