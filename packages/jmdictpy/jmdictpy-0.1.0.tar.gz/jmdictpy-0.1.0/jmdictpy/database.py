"""SQLite database builder and query engine"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Optional, Iterator

from .config import DB_PATH, ensure_data_dir
from .models import (
    Entry,
    Kanji,
    Kana,
    Sense,
    Gloss,
    Xref,
    LanguageSource,
    NameEntry,
    Character,
)

logger = logging.getLogger(__name__)


class DatabaseBuilder:
    """Builds SQLite database from JSON dictionary data"""
    
    SCHEMA = """
    -- JMdict entries (full JSON stored for flexibility)
    CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    );
    
    -- Kanji text index for fast lookup
    CREATE TABLE IF NOT EXISTS kanji_index (
        text TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        common INTEGER DEFAULT 0,
        FOREIGN KEY (entry_id) REFERENCES entries(id)
    );
    CREATE INDEX IF NOT EXISTS idx_kanji_text ON kanji_index(text);
    
    -- Kana text index for fast lookup
    CREATE TABLE IF NOT EXISTS kana_index (
        text TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        common INTEGER DEFAULT 0,
        FOREIGN KEY (entry_id) REFERENCES entries(id)
    );
    CREATE INDEX IF NOT EXISTS idx_kana_text ON kana_index(text);
    
    -- Gloss/meaning index for English lookup
    CREATE TABLE IF NOT EXISTS gloss_index (
        text TEXT NOT NULL,
        lang TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        FOREIGN KEY (entry_id) REFERENCES entries(id)
    );
    CREATE INDEX IF NOT EXISTS idx_gloss_text ON gloss_index(text);
    CREATE INDEX IF NOT EXISTS idx_gloss_lang ON gloss_index(lang);
    
    -- JMnedict name entries
    CREATE TABLE IF NOT EXISTS names (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS name_kanji_index (
        text TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        FOREIGN KEY (entry_id) REFERENCES names(id)
    );
    CREATE INDEX IF NOT EXISTS idx_name_kanji ON name_kanji_index(text);
    
    CREATE TABLE IF NOT EXISTS name_kana_index (
        text TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        FOREIGN KEY (entry_id) REFERENCES names(id)
    );
    CREATE INDEX IF NOT EXISTS idx_name_kana ON name_kana_index(text);
    
    -- Kanjidic characters
    CREATE TABLE IF NOT EXISTS characters (
        literal TEXT PRIMARY KEY,
        data TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS character_readings (
        reading TEXT NOT NULL,
        literal TEXT NOT NULL,
        type TEXT NOT NULL,
        FOREIGN KEY (literal) REFERENCES characters(literal)
    );
    CREATE INDEX IF NOT EXISTS idx_char_reading ON character_readings(reading);
    
    -- Metadata
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    
    -- Full-text search on glosses
    CREATE VIRTUAL TABLE IF NOT EXISTS gloss_fts USING fts5(
        text,
        entry_id,
        content='gloss_index',
        content_rowid='rowid'
    );
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
    
    def build(self, data: dict[str, dict], tags: Optional[dict] = None) -> Path:
        """
        Build SQLite database from dictionary data.
        
        Args:
            data: Dict with 'jmdict', 'jmnedict', 'kanjidic' keys
            tags: Tag definitions from JMdict
        
        Returns:
            Path to created database
        """
        ensure_data_dir()
        
        # Delete existing database
        if self.db_path.exists():
            self.db_path.unlink()
        
        logger.info(f"Building database: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Create schema
            conn.executescript(self.SCHEMA)
            
            # Build JMdict
            if "jmdict" in data:
                self._build_jmdict(conn, data["jmdict"])
            
            # Build JMnedict
            if "jmnedict" in data:
                self._build_jmnedict(conn, data["jmnedict"])
            
            # Build Kanjidic
            if "kanjidic" in data:
                self._build_kanjidic(conn, data["kanjidic"])
            
            # Store tags
            if tags:
                conn.execute(
                    "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                    ("tags", json.dumps(tags)),
                )
            
            # Populate FTS
            conn.execute("""
                INSERT INTO gloss_fts(rowid, text, entry_id)
                SELECT rowid, text, entry_id FROM gloss_index
            """)
            
            conn.commit()
            logger.info("Database build complete")
            
        finally:
            conn.close()
        
        return self.db_path
    
    def _build_jmdict(self, conn: sqlite3.Connection, data: dict):
        """Build JMdict tables"""
        words = data.get("words", [])
        tags = data.get("tags", {})
        
        logger.info(f"Building JMdict: {len(words)} entries")
        
        # Store tags
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ("jmdict_tags", json.dumps(tags)),
        )
        
        entries_batch = []
        kanji_batch = []
        kana_batch = []
        gloss_batch = []
        
        for word in words:
            entry_id = word["id"]
            entries_batch.append((entry_id, json.dumps(word)))
            
            # Index kanji
            for kanji in word.get("kanji", []):
                kanji_batch.append((
                    kanji["text"],
                    entry_id,
                    1 if kanji.get("common") else 0,
                ))
            
            # Index kana
            for kana in word.get("kana", []):
                kana_batch.append((
                    kana["text"],
                    entry_id,
                    1 if kana.get("common") else 0,
                ))
            
            # Index glosses
            for sense in word.get("sense", []):
                for gloss in sense.get("gloss", []):
                    gloss_batch.append((
                        gloss["text"],
                        gloss.get("lang", "eng"),
                        entry_id,
                    ))
        
        conn.executemany("INSERT INTO entries VALUES (?, ?)", entries_batch)
        conn.executemany("INSERT INTO kanji_index VALUES (?, ?, ?)", kanji_batch)
        conn.executemany("INSERT INTO kana_index VALUES (?, ?, ?)", kana_batch)
        conn.executemany("INSERT INTO gloss_index VALUES (?, ?, ?)", gloss_batch)
    
    def _build_jmnedict(self, conn: sqlite3.Connection, data: dict):
        """Build JMnedict tables"""
        words = data.get("words", [])
        logger.info(f"Building JMnedict: {len(words)} entries")
        
        names_batch = []
        kanji_batch = []
        kana_batch = []
        
        for word in words:
            entry_id = word["id"]
            names_batch.append((entry_id, json.dumps(word)))
            
            for kanji in word.get("kanji", []):
                kanji_batch.append((kanji["text"], entry_id))
            
            for kana in word.get("kana", []):
                kana_batch.append((kana["text"], entry_id))
        
        conn.executemany("INSERT INTO names VALUES (?, ?)", names_batch)
        conn.executemany("INSERT INTO name_kanji_index VALUES (?, ?)", kanji_batch)
        conn.executemany("INSERT INTO name_kana_index VALUES (?, ?)", kana_batch)
    
    def _build_kanjidic(self, conn: sqlite3.Connection, data: dict):
        """Build Kanjidic tables"""
        characters = data.get("characters", [])
        logger.info(f"Building Kanjidic: {len(characters)} entries")
        
        char_batch = []
        reading_batch = []
        
        for char in characters:
            literal = char["literal"]
            char_batch.append((literal, json.dumps(char)))
            
            # Index readings
            rm = char.get("readingMeaning")
            if rm:
                for group in rm.get("groups", []):
                    for reading in group.get("readings", []):
                        reading_batch.append((
                            reading["value"],
                            literal,
                            reading["type"],
                        ))
        
        conn.executemany("INSERT INTO characters VALUES (?, ?)", char_batch)
        conn.executemany("INSERT INTO character_readings VALUES (?, ?, ?)", reading_batch)


class Database:
    """Query engine for the JMdict SQLite database"""
    
    def __init__(self, db_path: Optional[Path] = None, memory_mode: bool = False):
        self.db_path = db_path or DB_PATH
        self.memory_mode = memory_mode
        self._conn: Optional[sqlite3.Connection] = None
        self._tags: Optional[dict] = None
    
    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database not found: {self.db_path}")
            
            if self.memory_mode:
                # Load entire database into memory
                file_conn = sqlite3.connect(self.db_path)
                self._conn = sqlite3.connect(":memory:")
                file_conn.backup(self._conn)
                file_conn.close()
                logger.info("Database loaded into memory")
            else:
                self._conn = sqlite3.connect(self.db_path)
            
            self._conn.row_factory = sqlite3.Row
        
        return self._conn
    
    @property
    def tags(self) -> dict:
        """Get tag definitions"""
        if self._tags is None:
            cursor = self.conn.execute(
                "SELECT value FROM metadata WHERE key = 'jmdict_tags'"
            )
            row = cursor.fetchone()
            self._tags = json.loads(row[0]) if row else {}
        return self._tags
    
    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def lookup_by_text(
        self,
        text: str,
        limit: int = 50,
    ) -> list[Entry]:
        """
        Lookup entries by kanji or kana text.
        
        Args:
            text: Text to search for (exact match)
            limit: Maximum results
        
        Returns:
            List of matching entries
        """
        # Try kanji first
        cursor = self.conn.execute(
            """
            SELECT DISTINCT e.data FROM entries e
            JOIN kanji_index ki ON e.id = ki.entry_id
            WHERE ki.text = ?
            LIMIT ?
            """,
            (text, limit),
        )
        results = [self._parse_entry(json.loads(row[0])) for row in cursor]
        
        if not results:
            # Try kana
            cursor = self.conn.execute(
                """
                SELECT DISTINCT e.data FROM entries e
                JOIN kana_index ki ON e.id = ki.entry_id
                WHERE ki.text = ?
                LIMIT ?
                """,
                (text, limit),
            )
            results = [self._parse_entry(json.loads(row[0])) for row in cursor]
        
        return results
    
    def lookup_by_reading(
        self,
        reading: str,
        limit: int = 50,
    ) -> list[Entry]:
        """Lookup entries by kana reading"""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT e.data FROM entries e
            JOIN kana_index ki ON e.id = ki.entry_id
            WHERE ki.text = ?
            LIMIT ?
            """,
            (reading, limit),
        )
        return [self._parse_entry(json.loads(row[0])) for row in cursor]
    
    def lookup_by_meaning(
        self,
        meaning: str,
        lang: str = "eng",
        limit: int = 50,
    ) -> list[Entry]:
        """Lookup entries by meaning/gloss (exact match)"""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT e.data FROM entries e
            JOIN gloss_index gi ON e.id = gi.entry_id
            WHERE gi.text = ? AND gi.lang = ?
            LIMIT ?
            """,
            (meaning, lang, limit),
        )
        return [self._parse_entry(json.loads(row[0])) for row in cursor]
    
    def search_meaning(
        self,
        query: str,
        lang: str = "eng",
        limit: int = 50,
    ) -> list[Entry]:
        """Search entries by meaning using full-text search"""
        cursor = self.conn.execute(
            """
            SELECT DISTINCT e.data FROM entries e
            JOIN gloss_fts fts ON e.id = fts.entry_id
            WHERE gloss_fts MATCH ?
            LIMIT ?
            """,
            (query, limit),
        )
        return [self._parse_entry(json.loads(row[0])) for row in cursor]
    
    def lookup_by_id(self, entry_id: str) -> Optional[Entry]:
        """Lookup entry by ID"""
        cursor = self.conn.execute(
            "SELECT data FROM entries WHERE id = ?",
            (entry_id,),
        )
        row = cursor.fetchone()
        if row:
            return self._parse_entry(json.loads(row[0]))
        return None
    
    def lookup_name(self, text: str, limit: int = 50) -> list[NameEntry]:
        """Lookup name entries"""
        # Try kanji
        cursor = self.conn.execute(
            """
            SELECT DISTINCT n.data FROM names n
            JOIN name_kanji_index ki ON n.id = ki.entry_id
            WHERE ki.text = ?
            LIMIT ?
            """,
            (text, limit),
        )
        results = [self._parse_name(json.loads(row[0])) for row in cursor]
        
        if not results:
            # Try kana
            cursor = self.conn.execute(
                """
                SELECT DISTINCT n.data FROM names n
                JOIN name_kana_index ki ON n.id = ki.entry_id
                WHERE ki.text = ?
                LIMIT ?
                """,
                (text, limit),
            )
            results = [self._parse_name(json.loads(row[0])) for row in cursor]
        
        return results
    
    def lookup_character(self, literal: str) -> Optional[Character]:
        """Lookup kanji character"""
        cursor = self.conn.execute(
            "SELECT data FROM characters WHERE literal = ?",
            (literal,),
        )
        row = cursor.fetchone()
        if row:
            return self._parse_character(json.loads(row[0]))
        return None
    
    def _parse_entry(self, data: dict) -> Entry:
        """Parse JSON entry to Entry model"""
        kanji = [
            Kanji(
                text=k["text"],
                common=k.get("common", False),
                tags=k.get("tags", []),
            )
            for k in data.get("kanji", [])
        ]
        
        kana = [
            Kana(
                text=k["text"],
                common=k.get("common", False),
                tags=k.get("tags", []),
                applies_to_kanji=k.get("appliesToKanji", ["*"]),
            )
            for k in data.get("kana", [])
        ]
        
        senses = []
        for s in data.get("sense", []):
            glosses = [
                Gloss(
                    text=g["text"],
                    lang=g.get("lang", "eng"),
                    type=g.get("type"),
                    gender=g.get("gender"),
                )
                for g in s.get("gloss", [])
            ]
            
            related = [self._parse_xref(x) for x in s.get("related", [])]
            antonym = [self._parse_xref(x) for x in s.get("antonym", [])]
            
            lang_source = [
                LanguageSource(
                    lang=ls.get("lang", "eng"),
                    full=ls.get("full", False),
                    wasei=ls.get("wasei", False),
                    text=ls.get("text"),
                )
                for ls in s.get("languageSource", [])
            ]
            
            senses.append(Sense(
                part_of_speech=s.get("partOfSpeech", []),
                glosses=glosses,
                fields=s.get("field", []),
                dialect=s.get("dialect", []),
                misc=s.get("misc", []),
                info=s.get("info", []),
                related=related,
                antonym=antonym,
                language_source=lang_source,
                applies_to_kanji=s.get("appliesToKanji", ["*"]),
                applies_to_kana=s.get("appliesToKana", ["*"]),
            ))
        
        return Entry(
            id=data["id"],
            kanji=kanji,
            kana=kana,
            senses=senses,
        )
    
    def _parse_xref(self, xref: list) -> Xref:
        """Parse cross-reference"""
        if len(xref) == 3:
            return Xref(kanji=xref[0], kana=xref[1], sense_index=xref[2])
        elif len(xref) == 2:
            if isinstance(xref[1], int):
                return Xref(kanji=xref[0], sense_index=xref[1])
            return Xref(kanji=xref[0], kana=xref[1])
        elif len(xref) == 1:
            return Xref(kanji=xref[0])
        return Xref()
    
    def _parse_name(self, data: dict) -> NameEntry:
        """Parse JMnedict entry"""
        kanji = [
            Kanji(text=k["text"], tags=k.get("tags", []))
            for k in data.get("kanji", [])
        ]
        kana = [
            Kana(
                text=k["text"],
                tags=k.get("tags", []),
                applies_to_kanji=k.get("appliesToKanji", ["*"]),
            )
            for k in data.get("kana", [])
        ]
        return NameEntry(
            id=data["id"],
            kanji=kanji,
            kana=kana,
            translations=data.get("translation", []),
        )
    
    def _parse_character(self, data: dict) -> Character:
        """Parse Kanjidic character"""
        rm = data.get("readingMeaning", {})
        readings_on = []
        readings_kun = []
        meanings = []
        
        for group in rm.get("groups", []):
            for reading in group.get("readings", []):
                if reading["type"] == "ja_on":
                    readings_on.append(reading["value"])
                elif reading["type"] == "ja_kun":
                    readings_kun.append(reading["value"])
            
            for meaning in group.get("meanings", []):
                if meaning.get("lang", "en") == "en":
                    meanings.append(meaning["value"])
        
        misc = data.get("misc", {})
        
        return Character(
            literal=data["literal"],
            readings_on=readings_on,
            readings_kun=readings_kun,
            meanings=meanings,
            grade=misc.get("grade"),
            stroke_count=misc.get("strokeCounts", [0])[0],
            jlpt_level=misc.get("jlptLevel"),
            frequency=misc.get("frequency"),
        )
