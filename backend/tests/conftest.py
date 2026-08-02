import os
import sys
from unittest.mock import MagicMock

# Mock fitz (PyMuPDF) dynamically to bypass heavy package installation timeouts
mock_fitz = MagicMock()
mock_doc = MagicMock()
mock_page = MagicMock()
mock_page.get_text.return_value = "Mock PDF extracted text"
mock_doc.__enter__.return_value = [mock_page]
mock_fitz.open.return_value = mock_doc
sys.modules["fitz"] = mock_fitz

# Mock language_tool_python dynamically to prevent downloading a heavy Java package
mock_lt = MagicMock()
mock_tool = MagicMock()
mock_tool.check.return_value = []
mock_lt.LanguageTool.return_value = mock_tool
sys.modules["language_tool_python"] = mock_lt

os.environ["TESTING"] = "True"

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 1. Create in-memory SQLite database engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Patch app.core.database globals BEFORE importing app models or endpoints
# This forces all background tasks and endpoints to use the test database
import app.core.database
app.core.database.engine = engine
app.core.database.SessionLocal = TestingSessionLocal

# 3. Now import app entities
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Fixture that provides a database session for testing and rolls back changes after.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """Fixture that overrides get_db to return the test session.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
