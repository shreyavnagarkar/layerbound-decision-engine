from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def make_job_config(**overrides):
    defaults = dict(
        job_id="JOB-001",
        requires_driving_licence=True,
        requires_shift_flexibility=True,
        requires_commute=True,
        salary_min=30000,
        salary_max=40000,
        max_notice_days=60,
    )
    defaults.update(overrides)
    return JobConfig(**defaults)


def make_candidate(**overrides):
    defaults = dict(
        candidate_id="CAND-001",
        job_id="JOB-001",
        has_driving_licence=True,
        willing_to_work_shifts=True,
        can_commute=True,
        expected_salary=35000,
        notice_period_days=30,
        fit_score=7,
    )
    defaults.update(overrides)
    return Candidate(**defaults)


def test_hard_rule_failure_short_circuits_scoring_and_sets_hard_reject_flag():
    job_config = make_job_config()
    candidate = make_candidate(has_driving_licence=False)

    result = evaluate_candidate(candidate, job_config)

    assert result.decision == "Reject"
    assert result.score == 0
    assert result.hard_reject is True
    assert "Missing driving licence" in result.issues
    assert result.score_breakdown == []


def test_candidate_passing_hard_rules_gets_scored_and_breakdown_populated():
    job_config = make_job_config()
    candidate = make_candidate()

    result = evaluate_candidate(candidate, job_config)

    assert result.hard_reject is False
    assert result.score > 0
    assert len(result.score_breakdown) > 0
    assert sum(item.points for item in result.score_breakdown) == result.score or result.score in (0, 100)


def test_full_end_to_end_matches_expected_shape():
    # Same scenario as the project's main.py demo.
    job_config = make_job_config()
    candidate = make_candidate(expected_salary=42000, notice_period_days=45, fit_score=7)

    result = evaluate_candidate(candidate, job_config)

    assert result.candidate_id == "CAND-001"
    assert result.job_id == "JOB-001"
    assert result.decision in ("Submit", "Review", "Reject")
    assert isinstance(result.summary, str) and len(result.summary) > 0


def test_summary_mentions_final_score():
    job_config = make_job_config()
    candidate = make_candidate()
    result = evaluate_candidate(candidate, job_config)
    assert str(result.score) in result.summary
