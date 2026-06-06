"""
conftest.py — Fixtures compartidos para todos los tests del backend.
pytest los descubre automáticamente; no hace falta importarlo.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Base de datos SQLite en memoria para tests (aislada por función)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_conftest.db"

_test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(scope="function")
def db():
    """
    Fixture 'db' esperado por test_models.py.
    Crea las tablas antes del test y las destruye al terminar,
    garantizando aislamiento total entre tests.
    """
    Base.metadata.create_all(bind=_test_engine)
    session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_test_engine)
