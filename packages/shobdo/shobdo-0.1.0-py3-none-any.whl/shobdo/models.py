from typing import List, Optional
from pydantic import BaseModel, Field

class Etymology(BaseModel):
    source_language: Optional[str] = Field(None, alias="source_language")
    derivation: Optional[str] = None

class Word(BaseModel):
    word: str
    pronunciation: Optional[str] = None
    etymology: Optional[Etymology] = None
    part_of_speech: Optional[str] = None
    meanings: List[str] = []
    english_translation: Optional[str] = None
    examples: List[str] = []
    
    def __str__(self):
        return f"{self.word} ({self.part_of_speech or 'N/A'}) - {self.english_translation or ''}"

    def formatted_meanings(self) -> str:
        """Returns a newline-separated string of meanings."""
        return "\n".join(f"{i+1}. {m}" for i, m in enumerate(self.meanings))
