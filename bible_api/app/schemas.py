from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class VerseBase(BaseModel):
    chapter: int
    verse: int
    text: str

class Verse(VerseBase):
    id: int
    book_id: int

    model_config = ConfigDict(from_attributes=True)

class BookBase(BaseModel):
    name: str
    abbreviation: str
    testament: str

class Book(BookBase):
    id: int
    verses: List[Verse] = []

    model_config = ConfigDict(from_attributes=True)

class BookReference(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
