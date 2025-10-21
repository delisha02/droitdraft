import os
from typing import Dict, Any
from app.agents.document_processor.docx_processor import extract_text_from_docx
from app.agents.document_processor.pdf_processor import extract_text_from_pdf
from app.agents.document_processor.ocr_processor import extract_text_from_image

class TextExtractor:
    """
    Extracts text from a file and retrieves document content.
    """
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieves the document content and metadata.
        For now, we assume the doc_id is the file path.
        """
        if not os.path.exists(doc_id):
            return None
        
        content = self.extract_text(doc_id)
        # In a real application, metadata would be stored in a database.
        # For now, we'll just return the file path as the id.
        return {
            "id": doc_id,
            "content": content,
            "metadata": {
                "file_path": doc_id
            }
        }

    def extract_text(self, file_path: str) -> str:
        """
        Extracts text from a file, automatically detecting the file type.
        """
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        if file_extension == ".docx":
            return extract_text_from_docx(file_path)
        elif file_extension == ".pdf":
            return extract_text_from_pdf(file_path)
        elif file_extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"]:
            return extract_text_from_image(file_path)
        else:
            print(f"Unsupported file type: {file_extension}")
            return ""
