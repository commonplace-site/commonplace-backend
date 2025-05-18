from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, Autoflush=False,bind=engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

BASE=declarative_base()