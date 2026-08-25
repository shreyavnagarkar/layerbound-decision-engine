import pytest

from src.engine.decision import get_decision
from src.models.job_config import JobConfig


@pytest.fixture()
def job_config():
    return JobConfig(
        job_id="JOB-001",
        salary_min=30000,
        salary_max=40000,
        max_notice_days=60,
        score_threshold_submit=80,
        score_threshold_review=50,
    )


def test_score_at_or_above_submit_threshold_is_submit(job_config):
    assert get_decision(80, job_config) == "Submit"
    assert get_decision(100, job_config) == "Submit"


def test_score_in_review_band(job_config):
    assert get_decision(50, job_config) == "Review"
    assert get_decision(79, job_config) == "Review"


def test_score_below_review_threshold_is_reject(job_config):
    assert get_decision(49, job_config) == "Reject"
    assert get_decision(0, job_config) == "Reject"


def test_custom_thresholds_are_respected():
    job_config = JobConfig(
        job_id="JOB-002",
        salary_min=0,
        salary_max=100000,
        max_notice_days=30,
        score_threshold_submit=90,
        score_threshold_review=60,
    )
    assert get_decision(85, job_config) == "Review"
    assert get_decision(90, job_config) == "Submit"
    assert get_decision(59, job_config) == "Reject"
