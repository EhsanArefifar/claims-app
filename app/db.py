import os
from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from fastapi import Depends

DATABASE_URL = os.environ["DATABASE_URL"]
Test_DATABASE_URL = os.environ["Test_DATABASE_URL"]

engine = create_engine(DATABASE_URL)
Test_engine = create_engine(Test_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Test_SessionLocal = sessionmaker(bind=Test_engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db        # ← hands the session to the route
    finally:
        db.close()      # ← runs after the route returns (even on exception)

def get_test_db():
    db = Test_SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
TestSessionDep = Annotated[Session, Depends(get_test_db)]