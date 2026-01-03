"""Main JMDict API - Jamdict-style interface"""

import logging
from pathlib import Path
from typing import Optional, Union

from .config import DB_PATH, DEFAULT_LANGUAGE, ensure_data_dir
from .database import Database, DatabaseBuilder
from .downloader import DownloadManager
from .models import Entry, NameEntry, Character, LookupResult
from .version import VersionManager, VersionInfo

logger = logging.getLogger(__name__)


class JMDict:
    """
    Main interface for JMdict dictionary lookups.
    
    Usage:
        >>> jmd = JMDict()  # Auto-downloads on first run
        >>> result = jmd.lookup("食べる")
        >>> for entry in result.entries:
        ...     print(entry)
    
    Args:
        db_path: Custom path to SQLite database
        language: Language for translations (default: "eng")
        auto_update: Check for updates on init (default: True)
        memory_mode: Load database into memory for faster queries
        common_only: Only download common words (smaller database)
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        language: str = DEFAULT_LANGUAGE,
        auto_update: bool = True,
        memory_mode: bool = False,
        common_only: bool = False,
    ):
        self.db_path = db_path or DB_PATH
        self.language = language
        self.memory_mode = memory_mode
        self.common_only = common_only
        
        self._version_manager = VersionManager()
        self._download_manager = DownloadManager()
        self._database: Optional[Database] = None
        
        # Ensure data directory exists
        ensure_data_dir()
        
        # Check if database exists, download if not
        if not self.db_path.exists():
            logger.info("Database not found, downloading...")
            self._download_and_build()
        elif auto_update:
            self._check_and_update()
    
    @property
    def database(self) -> Database:
        """Get database connection (lazy loading)"""
        if self._database is None:
            self._database = Database(self.db_path, self.memory_mode)
        return self._database
    
    @property
    def version(self) -> Optional[str]:
        """Get current database version"""
        info = self._version_manager.get_local_version()
        return info.tag if info else None
    
    @property
    def version_info(self) -> Optional[VersionInfo]:
        """Get full version information"""
        return self._version_manager.get_local_version()
    
    @property
    def tags(self) -> dict:
        """Get tag definitions (part of speech, dialects, etc.)"""
        return self.database.tags
    
    @property
    def ready(self) -> bool:
        """Check if database is ready for queries"""
        return self.db_path.exists()
    
    def lookup(
        self,
        query: str,
        limit: int = 50,
        include_names: bool = True,
        include_chars: bool = True,
    ) -> LookupResult:
        """
        Look up a word in the dictionary.
        
        This is the main search method. It searches:
        - JMdict entries by kanji and kana
        - JMnedict names (if include_names=True)
        - Kanjidic characters (if include_chars=True and query is a single kanji)
        
        Args:
            query: Text to search for (kanji, kana, or meaning)
            limit: Maximum number of results per category
            include_names: Include JMnedict name lookup
            include_chars: Include Kanjidic character lookup
        
        Returns:
            LookupResult containing entries, names, and characters
        """
        entries = self.database.lookup_by_text(query, limit)
        names = []
        characters = []
        
        if include_names and not entries:
            names = self.database.lookup_name(query, limit)
        
        if include_chars and len(query) == 1:
            char = self.database.lookup_character(query)
            if char:
                characters = [char]
        
        return LookupResult(entries=entries, names=names, characters=characters)
    
    def lookup_by_reading(self, reading: str, limit: int = 50) -> list[Entry]:
        """Look up entries by kana reading only"""
        return self.database.lookup_by_reading(reading, limit)
    
    def lookup_by_meaning(
        self,
        meaning: str,
        limit: int = 50,
    ) -> list[Entry]:
        """Look up entries by meaning (exact match)"""
        return self.database.lookup_by_meaning(meaning, self.language, limit)
    
    def search(self, query: str, limit: int = 50) -> list[Entry]:
        """
        Full-text search by meaning.
        
        Uses FTS5 for flexible matching (prefix, phrases, etc.)
        
        Args:
            query: Search query (e.g., "eat", "to eat", "eat*")
            limit: Maximum results
        
        Returns:
            List of matching entries
        """
        return self.database.search_meaning(query, self.language, limit)
    
    def lookup_by_id(self, entry_id: str) -> Optional[Entry]:
        """Look up entry by its JMdict ID"""
        return self.database.lookup_by_id(entry_id)
    
    def lookup_name(self, text: str, limit: int = 50) -> list[NameEntry]:
        """Look up names in JMnedict"""
        return self.database.lookup_name(text, limit)
    
    def lookup_character(self, char: str) -> Optional[Character]:
        """Look up a kanji character in Kanjidic"""
        if len(char) != 1:
            return None
        return self.database.lookup_character(char)
    
    def check_for_updates(self) -> tuple[Optional[str], Optional[str], bool]:
        """
        Check if updates are available.
        
        Returns:
            tuple: (local_version, remote_version, update_available)
        """
        return self._version_manager.check_for_updates()
    
    def update(
        self,
        force: bool = False,
        progress_callback=None,
    ) -> bool:
        """
        Update to the latest version.
        
        Args:
            force: Update even if already on latest version
            progress_callback: Optional callback(dict_name, downloaded, total)
        
        Returns:
            True if update was performed
        """
        local, remote, needs_update = self.check_for_updates()
        
        if not needs_update and not force:
            logger.info(f"Already on latest version: {local}")
            return False
        
        logger.info(f"Updating from {local} to {remote}")
        self._download_and_build(progress_callback)
        return True
    
    def _download_and_build(self, progress_callback=None):
        """Download dictionary files and build database"""
        # Close existing connection
        if self._database:
            self._database.close()
            self._database = None
        
        # Download
        data = self._download_manager.download_dictionary(
            language=self.language,
            common_only=self.common_only,
            progress_callback=progress_callback,
        )
        
        # Build database
        builder = DatabaseBuilder(self.db_path)
        tags = data.get("jmdict", {}).get("tags", {})
        builder.build(data, tags)
        
        # Save version info
        version_info = self._download_manager.get_version_from_data(data)
        self._version_manager.save_local_version(version_info)
        
        logger.info(f"Database updated to version: {version_info.tag}")
    
    def _check_and_update(self):
        """Check for updates and notify (don't auto-download)"""
        try:
            local, remote, needs_update = self.check_for_updates()
            if needs_update:
                logger.info(
                    f"Update available: {local} -> {remote}. "
                    f"Call jmd.update() to download."
                )
        except Exception as e:
            logger.debug(f"Update check failed: {e}")
    
    def close(self):
        """Close database connection"""
        if self._database:
            self._database.close()
            self._database = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        self.close()
