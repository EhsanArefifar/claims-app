import pytest
import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db, Base
from app.models import Customer, Policy

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Create schema once — only runs when a test actually requests db_session
@pytest.fixture(scope="session")
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


# Clean database before every test
@pytest.fixture()
def db_session(create_tables):

    session = TestingSessionLocal(bind=engine)

    for table in reversed(Base.metadata.sorted_tables):
        session.execute(
            text(
                f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'
            )
        )
    session.commit()

    yield session

    session.close()


# Seed required data
@pytest.fixture()
def seeded_db(db_session):
    customer = Customer(
        id = uuid.uuid4(),
        full_name= "Doe",
        email = "Doe@example.com",
        created_at = datetime.now()
    )

    db_session.add(customer)
    db_session.flush()

    policy = Policy(
        id = uuid.uuid4(),
        customer_id=customer.id,
        policy_number="POL-1001",
        type = "auto",
        status = "Submitted",
        start_date = "2026-01-01",
        created_at = datetime.now()
    )

    db_session.add(policy)
    db_session.commit()

    return {
        "customer": customer,
        "policy": policy,
    }


@pytest.fixture()
def client(db_session):
    def override_session():
        yield db_session

    app.dependency_overrides[get_db] = override_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_db():
    """TestClient with no DB dependency — for tests that are rejected by Pydantic
    before the database layer runs (e.g. missing required fields)."""
    with TestClient(app) as c:
        yield c