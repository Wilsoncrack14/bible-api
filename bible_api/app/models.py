from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    abbreviation = Column(String, unique=True, index=True)
    testament = Column(String)  # 'OT' or 'NT'

    verses = relationship("Verse", back_populates="book")

class Verse(Base):
    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    chapter = Column(Integer, index=True)
    verse = Column(Integer, index=True)
    text = Column(Text)

    book = relationship("Book", back_populates="verses")
