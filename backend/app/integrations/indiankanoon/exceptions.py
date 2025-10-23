
class IndianKanoonException(Exception):
    """Base exception for Indian Kanoon API client."""
    pass

class APIKeyNotFoundError(IndianKanoonException):
    """Raised when the Indian Kanoon API key is not found."""
    pass

class APIError(IndianKanoonException):
    """Raised when the API returns an error."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")
