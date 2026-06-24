from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///./bargues.db"

engine = create_engine(url=DB_URL, echo=False)
session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    db = session()
    try:
        yield db
    finally: db.close()