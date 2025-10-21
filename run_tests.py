import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path
import nltk

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt_tab') # Added punkt_tab
except LookupError:
    nltk.download('punkt_tab')

# Load environment variables from backend/.env
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Set PYTHONPATH to include the backend directory
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "backend")

# Run pytest for all backend tests
pytest_command = ["pytest", "backend/tests/"]
subprocess.run(pytest_command)
