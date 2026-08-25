import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api import app
from src.storage.db import Base, get_db


@pytest.fixture()
def db_session():
    """Fresh in-memory SQLite DB per test, so tests never share state."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_job_config():
    from src.models.job_config import JobConfig

    return JobConfig(
        job_id="JOB-001",
        title="Warehouse Operative",
        requires_driving_licence=True,
        requires_shift_flexibility=True,
        requires_commute=True,
        salary_min=30000,
        salary_max=40000,
        max_notice_days=60,
    )


@pytest.fixture()
def sample_candidate():
    from src.models.candidate import Candidate

    return Candidate(
        candidate_id="CAND-001",
        job_id="JOB-001",
        has_driving_licence=True,
        willing_to_work_shifts=True,
        can_commute=True,
        expected_salary=42000,
        notice_period_days=45,
        fit_score=7,
    )
