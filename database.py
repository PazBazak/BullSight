import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

database_url = os.environ["DATABASE_URL"]

engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        db.rollback()
    finally:
        db.close()
