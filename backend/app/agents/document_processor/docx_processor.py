import docx

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a .docx file.
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        # Handle exceptions for corrupted files or other issues
        print(f"Error processing .docx file: {e}")
        return ""
