"""Data models for JMdict entries"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Gloss:
    """Translation/meaning of a word"""
    text: str
    lang: str = "eng"
    type: Optional[str] = None
    gender: Optional[str] = None


@dataclass
class LanguageSource:
    """Source language info for borrowed words"""
    lang: str
    full: bool = False
    wasei: bool = False
    text: Optional[str] = None


@dataclass
class Xref:
    """Cross-reference to another entry"""
    kanji: Optional[str] = None
    kana: Optional[str] = None
    sense_index: Optional[int] = None
    
    def __str__(self):
        parts = []
        if self.kanji:
            parts.append(self.kanji)
        if self.kana:
            parts.append(self.kana)
        if self.sense_index:
            parts.append(f"[{self.sense_index}]")
        return "・".join(parts) if parts else ""


@dataclass
class Sense:
    """Sense/meaning element of an entry"""
    part_of_speech: list[str] = field(default_factory=list)
    glosses: list[Gloss] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)  # Field of use (math, comp, etc.)
    dialect: list[str] = field(default_factory=list)
    misc: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    related: list[Xref] = field(default_factory=list)
    antonym: list[Xref] = field(default_factory=list)
    language_source: list[LanguageSource] = field(default_factory=list)
    applies_to_kanji: list[str] = field(default_factory=list)
    applies_to_kana: list[str] = field(default_factory=list)
    
    def glosses_by_lang(self, lang: str = "eng") -> list[str]:
        """Get gloss texts for a specific language"""
        return [g.text for g in self.glosses if g.lang == lang]
    
    def __str__(self):
        texts = self.glosses_by_lang("eng")
        return "; ".join(texts) if texts else ""


@dataclass
class Kanji:
    """Kanji writing of a word"""
    text: str
    common: bool = False
    tags: list[str] = field(default_factory=list)
    
    def __str__(self):
        return self.text


@dataclass
class Kana:
    """Kana reading of a word"""
    text: str
    common: bool = False
    tags: list[str] = field(default_factory=list)
    applies_to_kanji: list[str] = field(default_factory=list)
    
    def __str__(self):
        return self.text


@dataclass
class Entry:
    """JMdict dictionary entry"""
    id: str
    kanji: list[Kanji] = field(default_factory=list)
    kana: list[Kana] = field(default_factory=list)
    senses: list[Sense] = field(default_factory=list)
    
    @property
    def is_common(self) -> bool:
        """Check if this entry is marked as common"""
        return any(k.common for k in self.kanji) or any(k.common for k in self.kana)
    
    @property
    def primary_kanji(self) -> Optional[str]:
        """Get primary kanji writing"""
        return self.kanji[0].text if self.kanji else None
    
    @property
    def primary_kana(self) -> Optional[str]:
        """Get primary kana reading"""
        return self.kana[0].text if self.kana else None
    
    @property
    def primary_reading(self) -> str:
        """Get primary reading (kanji or kana)"""
        return self.primary_kanji or self.primary_kana or ""
    
    def meanings(self, lang: str = "eng") -> list[str]:
        """Get all meanings for a specific language"""
        result = []
        for sense in self.senses:
            result.extend(sense.glosses_by_lang(lang))
        return result
    
    def __str__(self):
        reading = self.primary_reading
        if self.primary_kanji and self.primary_kana:
            reading = f"{self.primary_kanji}【{self.primary_kana}】"
        meanings = self.meanings()[:3]
        return f"{reading}: {'; '.join(meanings)}"


@dataclass
class NameEntry:
    """JMnedict name entry"""
    id: str
    kanji: list[Kanji] = field(default_factory=list)
    kana: list[Kana] = field(default_factory=list)
    translations: list[dict] = field(default_factory=list)
    
    @property
    def primary_kanji(self) -> Optional[str]:
        """Get primary kanji writing"""
        return self.kanji[0].text if self.kanji else None
    
    @property
    def primary_kana(self) -> Optional[str]:
        """Get primary kana reading"""
        return self.kana[0].text if self.kana else None
    
    @property
    def primary_reading(self) -> str:
        """Get primary reading (kanji or kana)"""
        return self.primary_kanji or self.primary_kana or ""
    
    @property
    def romaji(self) -> str:
        """Get romanized name"""
        if self.translations:
            trans = self.translations[0].get('translation', [])
            if trans:
                return trans[0].get('text', '')
        return ""
    
    @property
    def name_types(self) -> list[str]:
        """Get name types (surname, given, place, etc.)"""
        if self.translations:
            return self.translations[0].get('type', [])
        return []
    
    def __str__(self):
        kanji = self.primary_kanji or ""
        kana = self.primary_kana or ""
        romaji = self.romaji
        types = ", ".join(self.name_types)
        
        if kanji and kana:
            result = f"{kanji}【{kana}】"
        else:
            result = kanji or kana
        
        if romaji:
            result += f" - {romaji}"
        if types:
            result += f" ({types})"
        
        return result


@dataclass
class Character:
    """Kanjidic character entry"""
    literal: str
    readings_on: list[str] = field(default_factory=list)
    readings_kun: list[str] = field(default_factory=list)
    meanings: list[str] = field(default_factory=list)
    grade: Optional[int] = None
    stroke_count: int = 0
    jlpt_level: Optional[int] = None
    frequency: Optional[int] = None
    
    def __str__(self):
        return f"{self.literal}: {', '.join(self.meanings[:3])}"


@dataclass
class LookupResult:
    """Result of a dictionary lookup"""
    entries: list[Entry] = field(default_factory=list)
    names: list[NameEntry] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    
    def __bool__(self):
        return bool(self.entries or self.names or self.characters)
    
    def __len__(self):
        return len(self.entries) + len(self.names) + len(self.characters)
    
    @property
    def is_empty(self) -> bool:
        return not self
    
    def __str__(self):
        parts = []
        if self.entries:
            parts.append(f"{len(self.entries)} entries")
        if self.names:
            parts.append(f"{len(self.names)} names")
        if self.characters:
            parts.append(f"{len(self.characters)} characters")
        return f"LookupResult({', '.join(parts) or 'empty'})"
