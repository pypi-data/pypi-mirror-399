"""Configuration and paths for PyJMDict"""

from pathlib import Path
import os

# Data directory
DATA_DIR = Path(os.environ.get("JMDICTPY_DATA_DIR", Path.home() / ".jmdictpy"))

# Database paths
DB_PATH = DATA_DIR / "jmdict.db"
VERSION_FILE = DATA_DIR / "version.json"

# GitHub API
GITHUB_API_LATEST = "https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest"
GITHUB_REPO = "scriptin/jmdict-simplified"

# Supported languages (ISO 639-2 codes)
SUPPORTED_LANGUAGES = {
    "all": "All languages",
    "eng": "English",
    "ger": "German",
    "rus": "Russian",
    "hun": "Hungarian",
    "dut": "Dutch",
    "spa": "Spanish",
    "fre": "French",
    "swe": "Swedish",
    "slv": "Slovenian",
}

# Default language
DEFAULT_LANGUAGE = "eng"

# Download settings
DOWNLOAD_TIMEOUT = 60
CHUNK_SIZE = 8192

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR
