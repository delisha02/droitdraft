import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Set PYTHONPATH to include the backend directory
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "backend")

# Run pytest for only the integration test
pytest_command = ["pytest", "backend/tests/integration/test_chromadb_integration.py"]
subprocess.run(pytest_command)
