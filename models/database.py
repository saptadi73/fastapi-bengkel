from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#
URL_DATABASE = 'postgresql+psycopg2://openpg:openpgpwd@localhost:5432/bengkel'
# URL_DATABASE = 'postgresql+psycopg2://pgwarga:pgw4rg4PWD@103.160.213.59:5432/bengkel'

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
