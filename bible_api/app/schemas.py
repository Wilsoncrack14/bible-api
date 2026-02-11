from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

class VerseBase(BaseModel):
    chapter: int
    verse: int
    text: str

class Verse(VerseBase):
    id: int
    book_id: int

    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('text')
    @classmethod
    def normalize_capitalization(cls, v: str) -> str:
        """
        Normaliza el texto eliminando palabras completamente en mayúsculas.
        Solo convierte a minúsculas las palabras que están completamente en mayúsculas
        (de 2 o más letras), manteniendo los nombres propios y otras capitalizaciones.
        """
        if not v:
            return v
        
        words = v.split()
        normalized_words = []
        
        for i, word in enumerate(words):
            # Separar la palabra de la puntuación
            # Buscar dónde termina la palabra alfabética
            alpha_end = 0
            for j, char in enumerate(word):
                if char.isalpha():
                    alpha_end = j + 1
                elif alpha_end > 0:
                    break
            
            if alpha_end == 0:
                normalized_words.append(word)
                continue
                
            word_part = word[:alpha_end]
            punct_part = word[alpha_end:]
            
            # Solo convertir palabras de 2+ letras que están completamente en mayúsculas
            if len(word_part) >= 2 and word_part.isupper():
                # Mantener la primera letra en mayúscula si es la primera palabra
                if i == 0:
                    normalized_words.append(word_part.capitalize() + punct_part)
                else:
                    normalized_words.append(word_part.lower() + punct_part)
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)

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
