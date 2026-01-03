"""
JMdictPy - Fast Python wrapper for JMdict with SQLite backend

Usage:
    from jmdictpy import JMDict
    
    jmd = JMDict()  # Auto-downloads and builds DB on first run
    
    result = jmd.lookup("食べる")
    for entry in result.entries:
        print(entry.kanji, entry.kana, entry.senses)
"""

__version__ = "0.1.0"

from .api import JMDict
from .models import (
    Entry,
    Kanji,
    Kana,
    Sense,
    Gloss,
    LookupResult,
)

__all__ = [
    "JMDict",
    "Entry",
    "Kanji",
    "Kana",
    "Sense",
    "Gloss",
    "LookupResult",
    "__version__",
]
