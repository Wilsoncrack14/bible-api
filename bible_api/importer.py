import json
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Book, Verse

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def import_data():
    db = SessionLocal()
    try:
        with open("bible_api/data/es_rvr.json", "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        # JSON structure (based on thiagobodruk/bible):
        # [
        #   {
        #       "abbrev": "gn",
        #       "book": "Génesis",
        #       "chapters": [
        #           ["verse 1", "verse 2", ...],
        #           ...
        #       ]
        #   },
        #   ...
        # ]

        print(f"Found {len(data)} books.")
        
        for book_idx, book_data in enumerate(data):
            # Check if book exists
            db_book = db.query(Book).filter(Book.name == book_data["name"]).first()
            if not db_book:
                # Testament logic (simple approach: first 39 are OT)
                testament = "OT" if book_idx < 39 else "NT"
                
                db_book = Book(
                    name=book_data["name"],
                    abbreviation=book_data["abbrev"],
                    testament=testament
                )
                db.add(db_book)
                db.commit()
                db.refresh(db_book)
                print(f"Importing {db_book.name}...")

            for ch_idx, verses in enumerate(book_data["chapters"]):
                chapter_num = ch_idx + 1
                for v_idx, verse_text in enumerate(verses):
                    verse_num = v_idx + 1
                    
                    # Check if verse exists to avoid duplicates if re-run
                    existing_verse = db.query(Verse).filter(
                        Verse.book_id == db_book.id,
                        Verse.chapter == chapter_num,
                        Verse.verse == verse_num
                    ).first()
                    
                    if not existing_verse:
                        db_verse = Verse(
                            book_id=db_book.id,
                            chapter=chapter_num,
                            verse=verse_num,
                            text=verse_text
                        )
                        db.add(db_verse)
                
                db.commit() # Commit per chapter

        print("Import completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
