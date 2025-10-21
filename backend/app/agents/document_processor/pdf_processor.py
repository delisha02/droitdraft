import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a text-based PDF file.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = []
            for page in pdf.pages:
                full_text.append(page.extract_text())
            return "\n".join(full_text)
    except Exception as e:
        # Handle exceptions for corrupted files or other issues
        print(f"Error processing .pdf file: {e}")
        return ""
