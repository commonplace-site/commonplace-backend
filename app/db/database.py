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


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("WARNING: DATABASE_URL environment variable not set. Using default SQLite database.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()