# core/db_utils.py
from contextlib import contextmanager
from db.database import SessionLocal

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
