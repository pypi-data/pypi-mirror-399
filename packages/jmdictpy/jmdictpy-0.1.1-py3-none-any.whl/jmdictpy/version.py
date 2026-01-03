"""Version management and update checking"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

from .config import (
    GITHUB_API_LATEST,
    VERSION_FILE,
    DOWNLOAD_TIMEOUT,
    ensure_data_dir,
)

logger = logging.getLogger(__name__)


class VersionInfo:
    """Version information container"""
    
    def __init__(
        self,
        tag: str,
        published_at: Optional[str] = None,
        dict_date: Optional[str] = None,
        languages: Optional[list[str]] = None,
        common_only: bool = False,
    ):
        self.tag = tag
        self.published_at = published_at
        self.dict_date = dict_date
        self.languages = languages or ["eng"]
        self.common_only = common_only
    
    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "published_at": self.published_at,
            "dict_date": self.dict_date,
            "languages": self.languages,
            "common_only": self.common_only,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VersionInfo":
        return cls(
            tag=data.get("tag", "unknown"),
            published_at=data.get("published_at"),
            dict_date=data.get("dict_date"),
            languages=data.get("languages", ["eng"]),
            common_only=data.get("common_only", False),
        )
    
    def __str__(self):
        return self.tag
    
    def __eq__(self, other):
        if isinstance(other, VersionInfo):
            return self.tag == other.tag
        return self.tag == str(other)


class VersionManager:
    """Manages version checking and updates"""
    
    def __init__(self, version_file: Optional[Path] = None):
        self.version_file = version_file or VERSION_FILE
        self._cached_remote: Optional[dict] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=1)
    
    def get_local_version(self) -> Optional[VersionInfo]:
        """Get locally installed version"""
        if not self.version_file.exists():
            return None
        
        try:
            with open(self.version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return VersionInfo.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read version file: {e}")
            return None
    
    def save_local_version(self, version: VersionInfo):
        """Save version info to local file"""
        ensure_data_dir()
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(version.to_dict(), f, indent=2)
    
    def get_remote_release(self, force_refresh: bool = False) -> Optional[dict]:
        """Fetch latest release info from GitHub API"""
        # Check cache
        if not force_refresh and self._cached_remote and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return self._cached_remote
        
        try:
            response = requests.get(
                GITHUB_API_LATEST,
                timeout=DOWNLOAD_TIMEOUT,
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            response.raise_for_status()
            self._cached_remote = response.json()
            self._cache_time = datetime.now()
            return self._cached_remote
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch remote version: {e}")
            return None
    
    def get_remote_version(self, force_refresh: bool = False) -> Optional[str]:
        """Get latest version tag from GitHub"""
        release = self.get_remote_release(force_refresh)
        if release:
            return release.get("tag_name")
        return None
    
    def check_for_updates(self) -> tuple[Optional[str], Optional[str], bool]:
        """
        Check if updates are available.
        
        Returns:
            tuple: (local_version, remote_version, update_available)
        """
        local = self.get_local_version()
        remote = self.get_remote_version()
        
        local_tag = local.tag if local else None
        update_available = False
        
        if remote and local_tag:
            update_available = remote != local_tag
        elif remote and not local_tag:
            update_available = True
        
        return local_tag, remote, update_available
    
    def needs_update(self) -> bool:
        """Quick check if update is needed"""
        _, _, update_available = self.check_for_updates()
        return update_available
    
    def is_installed(self) -> bool:
        """Check if dictionary is installed"""
        return self.get_local_version() is not None
    
    def get_download_urls(self, language: str = "eng", common_only: bool = False) -> dict:
        """Get download URLs for dictionary files from latest release"""
        release = self.get_remote_release()
        if not release:
            return {}
        
        tag = release.get("tag_name", "")
        assets = release.get("assets", [])
        
        urls = {}
        
        # Build expected filename patterns
        jmdict_pattern = f"jmdict-{language}"
        if common_only and language == "eng":
            jmdict_pattern = "jmdict-eng-common"
        
        for asset in assets:
            name = asset.get("name", "")
            download_url = asset.get("browser_download_url", "")
            
            # Match JMdict
            if name.startswith(jmdict_pattern) and name.endswith(".json.zip"):
                urls["jmdict"] = download_url
            
            # Match JMnedict (English only)
            if name.startswith("jmnedict-all") and name.endswith(".json.zip"):
                urls["jmnedict"] = download_url
            
            # Match Kanjidic
            kanjidic_lang = language[:2] if language != "all" else "all"
            if language == "eng":
                kanjidic_lang = "en"
            if name.startswith(f"kanjidic2-{kanjidic_lang}") and name.endswith(".json.zip"):
                urls["kanjidic"] = download_url
            elif name.startswith("kanjidic2-all") and name.endswith(".json.zip"):
                if "kanjidic" not in urls:
                    urls["kanjidic"] = download_url
        
        return urls
