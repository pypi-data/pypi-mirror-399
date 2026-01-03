"""Tests for JMdictPy"""

import json
import tempfile
from pathlib import Path

import pytest

from jmdictpy.models import Entry, Kanji, Kana, Sense, Gloss, LookupResult
from jmdictpy.database import DatabaseBuilder, Database
from jmdictpy.version import VersionManager, VersionInfo


class TestModels:
    """Test data models"""
    
    def test_entry_creation(self):
        entry = Entry(
            id="1234",
            kanji=[Kanji(text="食べる", common=True)],
            kana=[Kana(text="たべる", common=True)],
            senses=[
                Sense(
                    part_of_speech=["v1"],
                    glosses=[Gloss(text="to eat", lang="eng")],
                )
            ],
        )
        
        assert entry.id == "1234"
        assert entry.primary_kanji == "食べる"
        assert entry.primary_kana == "たべる"
        assert entry.is_common is True
        assert len(entry.meanings()) == 1
        assert "to eat" in entry.meanings()
    
    def test_entry_kana_only(self):
        entry = Entry(
            id="5678",
            kanji=[],
            kana=[Kana(text="すごい", common=True)],
            senses=[
                Sense(glosses=[Gloss(text="amazing", lang="eng")]),
            ],
        )
        
        assert entry.primary_kanji is None
        assert entry.primary_reading == "すごい"
    
    def test_lookup_result(self):
        result = LookupResult(
            entries=[Entry(id="1", kanji=[], kana=[], senses=[])],
        )
        
        assert len(result) == 1
        assert bool(result) is True
        assert result.is_empty is False
    
    def test_empty_lookup_result(self):
        result = LookupResult()
        
        assert len(result) == 0
        assert bool(result) is False
        assert result.is_empty is True


class TestDatabase:
    """Test database building and querying"""
    
    @pytest.fixture
    def sample_jmdict_data(self):
        return {
            "version": "3.6.1",
            "languages": ["eng"],
            "commonOnly": False,
            "dictDate": "2025-12-29",
            "dictRevisions": ["1.09"],
            "tags": {
                "v1": "Ichidan verb",
                "n": "noun",
            },
            "words": [
                {
                    "id": "1358280",
                    "kanji": [{"text": "食べる", "common": True, "tags": []}],
                    "kana": [{"text": "たべる", "common": True, "tags": [], "appliesToKanji": ["*"]}],
                    "sense": [
                        {
                            "partOfSpeech": ["v1", "vt"],
                            "appliesToKanji": ["*"],
                            "appliesToKana": ["*"],
                            "related": [],
                            "antonym": [],
                            "field": [],
                            "dialect": [],
                            "misc": [],
                            "info": [],
                            "languageSource": [],
                            "gloss": [
                                {"text": "to eat", "lang": "eng", "gender": None, "type": None}
                            ],
                        }
                    ],
                },
                {
                    "id": "1002360",
                    "kanji": [{"text": "行く", "common": True, "tags": []}],
                    "kana": [{"text": "いく", "common": True, "tags": [], "appliesToKanji": ["*"]}],
                    "sense": [
                        {
                            "partOfSpeech": ["v5k-s", "vi"],
                            "appliesToKanji": ["*"],
                            "appliesToKana": ["*"],
                            "related": [],
                            "antonym": [],
                            "field": [],
                            "dialect": [],
                            "misc": [],
                            "info": [],
                            "languageSource": [],
                            "gloss": [
                                {"text": "to go", "lang": "eng", "gender": None, "type": None}
                            ],
                        }
                    ],
                },
            ],
        }
    
    @pytest.fixture
    def temp_db(self, sample_jmdict_data):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            builder = DatabaseBuilder(db_path)
            builder.build({"jmdict": sample_jmdict_data})
            yield db_path
    
    def test_database_build(self, temp_db):
        assert temp_db.exists()
        
        db = Database(temp_db)
        try:
            # Test lookup
            entries = db.lookup_by_text("食べる")
            assert len(entries) == 1
            assert entries[0].id == "1358280"
        finally:
            db.close()
    
    def test_lookup_by_kana(self, temp_db):
        db = Database(temp_db)
        try:
            entries = db.lookup_by_reading("たべる")
            assert len(entries) == 1
            assert entries[0].primary_kanji == "食べる"
        finally:
            db.close()
    
    def test_lookup_by_meaning(self, temp_db):
        db = Database(temp_db)
        try:
            entries = db.lookup_by_meaning("to eat")
            assert len(entries) == 1
            assert entries[0].primary_kanji == "食べる"
        finally:
            db.close()
    
    def test_lookup_no_results(self, temp_db):
        db = Database(temp_db)
        try:
            entries = db.lookup_by_text("存在しない")
            assert len(entries) == 0
        finally:
            db.close()


class TestVersionManager:
    """Test version management"""
    
    def test_version_info_creation(self):
        info = VersionInfo(
            tag="3.6.1+20251229123436",
            dict_date="2025-12-29",
            languages=["eng"],
        )
        
        assert info.tag == "3.6.1+20251229123436"
        assert str(info) == "3.6.1+20251229123436"
    
    def test_version_info_serialization(self):
        info = VersionInfo(
            tag="3.6.1+20251229123436",
            dict_date="2025-12-29",
        )
        
        data = info.to_dict()
        restored = VersionInfo.from_dict(data)
        
        assert restored.tag == info.tag
        assert restored.dict_date == info.dict_date
    
    def test_version_equality(self):
        info1 = VersionInfo(tag="3.6.1")
        info2 = VersionInfo(tag="3.6.1")
        info3 = VersionInfo(tag="3.6.2")
        
        assert info1 == info2
        assert info1 != info3
        assert info1 == "3.6.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
