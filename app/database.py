from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from typing import List, Optional
from . import utils
from . import schemas
from fastapi import Body, Depends, FastAPI, HTTPException, Response, status
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from .config import settings

# connection string
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}/{settings.database_name}"

# creating the engine (creates the connection)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create a session when you want to talk to the db.
# autocommit=False - disables automatic commits after every query
# autoflush=False - disables automatic flushing of the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# define the base class for all ORM models
Base = declarative_base()

# dependency - The function get_db() is typically used as a dependency in your route handlers to provide the session for interacting with the database. This ensures that each incoming request gets a fresh session, and the session is cleaned up properly after the request.
def get_db():
    # create a new database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# database connection - Keep trying to connect (after every 2 sec) until success
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='Social Media FastAPI', user='postgres',     password='39413004', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('Database connected successfully!!')
#         break
#     except Exception as error:
#         print('Database connection failed!!')
#         print('Error:', error)
#         time.sleep(2)

