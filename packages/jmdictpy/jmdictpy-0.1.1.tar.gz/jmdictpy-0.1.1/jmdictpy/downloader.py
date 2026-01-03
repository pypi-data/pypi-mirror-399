"""Download manager for fetching dictionary files from GitHub releases"""

import io
import json
import logging
import zipfile
from pathlib import Path
from typing import Optional, Callable

import requests

from .config import (
    DATA_DIR,
    DOWNLOAD_TIMEOUT,
    CHUNK_SIZE,
    ensure_data_dir,
)
from .version import VersionManager, VersionInfo

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manages downloading and extracting dictionary files"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.version_manager = VersionManager()
    
    def download_file(
        self,
        url: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bytes:
        """
        Download a file from URL.
        
        Args:
            url: URL to download
            progress_callback: Optional callback(downloaded_bytes, total_bytes)
        
        Returns:
            File contents as bytes
        """
        logger.info(f"Downloading: {url}")
        
        response = requests.get(
            url,
            timeout=DOWNLOAD_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        chunks = []
        
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                chunks.append(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size:
                    progress_callback(downloaded, total_size)
        
        return b"".join(chunks)
    
    def download_and_extract_json(
        self,
        url: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> dict:
        """
        Download a .json.zip file and extract the JSON content.
        
        Args:
            url: URL to download
            progress_callback: Optional progress callback
        
        Returns:
            Parsed JSON data
        """
        data = self.download_file(url, progress_callback)
        
        # Extract from zip
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            # Get the first .json file in the archive
            json_files = [n for n in zf.namelist() if n.endswith(".json")]
            if not json_files:
                raise ValueError("No JSON file found in archive")
            
            logger.info(f"Extracting: {json_files[0]}")
            with zf.open(json_files[0]) as f:
                return json.load(f)
    
    def download_dictionary(
        self,
        language: str = "eng",
        common_only: bool = False,
        include_names: bool = True,
        include_kanji: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> dict[str, dict]:
        """
        Download all dictionary files.
        
        Args:
            language: Language code (eng, ger, etc.)
            common_only: Only download common words (smaller file)
            include_names: Include JMnedict names dictionary
            include_kanji: Include Kanjidic character dictionary
            progress_callback: Optional callback(dict_name, downloaded, total)
        
        Returns:
            Dict mapping dict names to parsed JSON data
        """
        ensure_data_dir()
        
        urls = self.version_manager.get_download_urls(language, common_only)
        if not urls:
            raise RuntimeError("Failed to get download URLs from GitHub")
        
        results = {}
        
        # Download JMdict (required)
        if "jmdict" in urls:
            def jmdict_progress(d, t):
                if progress_callback:
                    progress_callback("JMdict", d, t)
            
            results["jmdict"] = self.download_and_extract_json(
                urls["jmdict"], jmdict_progress
            )
            logger.info(f"Downloaded JMdict: {len(results['jmdict'].get('words', []))} entries")
        else:
            raise RuntimeError(f"JMdict not found for language: {language}")
        
        # Download JMnedict (optional)
        if include_names and "jmnedict" in urls:
            def jmnedict_progress(d, t):
                if progress_callback:
                    progress_callback("JMnedict", d, t)
            
            try:
                results["jmnedict"] = self.download_and_extract_json(
                    urls["jmnedict"], jmnedict_progress
                )
                logger.info(f"Downloaded JMnedict: {len(results['jmnedict'].get('words', []))} entries")
            except Exception as e:
                logger.warning(f"Failed to download JMnedict: {e}")
        
        # Download Kanjidic (optional)
        if include_kanji and "kanjidic" in urls:
            def kanjidic_progress(d, t):
                if progress_callback:
                    progress_callback("Kanjidic", d, t)
            
            try:
                results["kanjidic"] = self.download_and_extract_json(
                    urls["kanjidic"], kanjidic_progress
                )
                logger.info(f"Downloaded Kanjidic: {len(results['kanjidic'].get('characters', []))} entries")
            except Exception as e:
                logger.warning(f"Failed to download Kanjidic: {e}")
        
        return results
    
    def get_version_from_data(self, data: dict) -> VersionInfo:
        """Extract version info from downloaded dictionary data"""
        jmdict_data = data.get("jmdict", {})
        
        return VersionInfo(
            tag=self.version_manager.get_remote_version() or "unknown",
            published_at=None,
            dict_date=jmdict_data.get("dictDate"),
            languages=jmdict_data.get("languages", ["eng"]),
            common_only=jmdict_data.get("commonOnly", False),
        )
