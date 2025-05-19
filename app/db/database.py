# from sqlalchemy import  create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL=os.getenv("DATABASE_URL")
# engine = create_engine(DATABASE_URL)
# # SessionLocal = sessionmaker(autocommit=False, Autoflush=False,bind=engine)
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# BASE=declarative_base()


import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL configuration
DATABASE_URL = "postgresql://commonplace_pdm3_user:oZkVyRxuB7GcFbYrzJQqCU815pwNfTSU@dpg-d01j9hadbo4c738qlva0-a.oregon-postgres.render.com/commonplace_pdm3"

engine = create_engine(DATABASE_URL, pool_size=5 ,max_overflow=10, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()