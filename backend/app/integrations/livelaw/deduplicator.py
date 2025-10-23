
import hashlib

def generate_fingerprint(content: str) -> str:
    """Generates a fingerprint for the given content using SHA256."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
