import os
from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from fastapi import Depends

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db        # ← hands the session to the route
    finally:
        db.close()      # ← runs after the route returns (even on exception)


SessionDep = Annotated[Session, Depends(get_db)]