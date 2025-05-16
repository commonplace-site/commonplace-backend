from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
# DATABASE_URL=os.getenv("DATABASE_URL")
# DATABASE_URL="postgresql://commonplace_pdm3_user:oZkVyRxuB7GcFbYrzJQqCU815pwNfTSU@dpg-d01j9hadbo4c738qlva0-a.oregon-postgres.render.com/commonplace_pdm3"
DATABASE_URL="postgresql://postgres:junaid@localhost:5432/commonplace"
engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, Autoflush=False,bind=engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

BASE=declarative_base()