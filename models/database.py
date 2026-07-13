from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
URL_DATABASE = os.getenv('DATABASE_URL', 'postgresql+psycopg2://openpg:openpgpwd@localhost:5432/bengkel')

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(db):
    db.execute(text("SELECT 1"))
    bind = db.get_bind()
    dialect = getattr(getattr(bind, "dialect", None), "name", "unknown")
    database_name = getattr(getattr(bind, "url", None), "database", None)

    return {
        "connected": True,
        "dialect": dialect,
        "database": database_name,
    }
