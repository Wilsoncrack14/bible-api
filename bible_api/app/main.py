from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bible API", description="API showing the complete Reina Valera 1960 Bible", version="1.0.0")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bible API"}

@app.get("/books", response_model=List[schemas.BookReference])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books

# Simple in-memory cache
CHAPTER_CACHE = {}

@app.get("/books/{book_id}/chapters/{chapter}", response_model=List[schemas.Verse])
def read_chapter(book_id: int, chapter: int, db: Session = Depends(get_db)):
    cache_key = (book_id, chapter)
    if cache_key in CHAPTER_CACHE:
        return CHAPTER_CACHE[cache_key]

    verses = db.query(models.Verse).filter(models.Verse.book_id == book_id, models.Verse.chapter == chapter).all()
    if not verses:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Convert to Pydantic models for caching
    validated_verses = [schemas.Verse.model_validate(v) for v in verses]
    CHAPTER_CACHE[cache_key] = validated_verses
    
    return validated_verses

@app.get("/books/{book_id}/chapters/{chapter}/verses/{verse}", response_model=schemas.Verse)
def read_verse(book_id: int, chapter: int, verse: int, db: Session = Depends(get_db)):
    verse_obj = db.query(models.Verse).filter(
        models.Verse.book_id == book_id, 
        models.Verse.chapter == chapter, 
        models.Verse.verse == verse
    ).first()
    if not verse_obj:
        raise HTTPException(status_code=404, detail="Verse not found")
    return verse_obj

@app.get("/search", response_model=List[schemas.Verse])
def search_verses(q: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    verses = db.query(models.Verse).filter(models.Verse.text.contains(q)).offset(skip).limit(limit).all()
    return verses

@app.get("/random", response_model=schemas.Verse)
def random_verse(db: Session = Depends(get_db)):
    import random
    count = db.query(models.Verse).count()
    if count == 0:
        raise HTTPException(status_code=404, detail="No verses found")
    random_offset = random.randint(0, count - 1)
    verse = db.query(models.Verse).offset(random_offset).first()
    return verse
