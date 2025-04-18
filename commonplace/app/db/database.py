from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# DATABASE_URL=os.getenv("DATABASE_URL")
DATABASE_URL="postgresql://postgres:junaid@localhost:5432/commonplace"
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, Autoflush=False,bind=engine)
BASE=declarative_base()