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
from dotenv import load_dotenv
# Database URL configuration
# DATABASE_URL = "postgresql://root:commonplace_root@66.94.110.158:5432/commonplace_root"
load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_size=5 ,max_overflow=10, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()