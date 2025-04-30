from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# DATABASE_URL=os.getenv("DATABASE_URL")
DATABASE_URL="postgresql://postgres:junaid@localhost:5432/commonplace"
engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, Autoflush=False,bind=engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

BASE=declarative_base()