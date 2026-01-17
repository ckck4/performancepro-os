# db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# SQLite database stored in the project root
DATABASE_URL = "sqlite:///performancepro.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db() -> None:
    """Create all tables defined in models.py."""
    Base.metadata.create_all(bind=engine)
