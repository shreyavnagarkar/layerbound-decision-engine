from src.engine.rules import check_hard_rules
from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def make_job_config(**overrides):
    defaults = dict(
        job_id="JOB-001",
        requires_driving_licence=False,
        requires_shift_flexibility=False,
        requires_commute=False,
        salary_min=30000,
        salary_max=40000,
        max_notice_days=60,
    )
    defaults.update(overrides)
    return JobConfig(**defaults)


def make_candidate(**overrides):
    defaults = dict(candidate_id="CAND-001", job_id="JOB-001")
    defaults.update(overrides)
    return Candidate(**defaults)


def test_no_issues_when_nothing_required():
    job_config = make_job_config()
    candidate = make_candidate()
    assert check_hard_rules(candidate, job_config) == []


def test_missing_driving_licence_flagged_when_required():
    job_config = make_job_config(requires_driving_licence=True)
    candidate = make_candidate(has_driving_licence=False)
    assert "Missing driving licence" in check_hard_rules(candidate, job_config)


def test_missing_driving_licence_not_flagged_when_not_required():
    job_config = make_job_config(requires_driving_licence=False)
    candidate = make_candidate(has_driving_licence=False)
    assert check_hard_rules(candidate, job_config) == []


def test_unanswered_field_treated_as_failing_a_required_check():
    # has_driving_licence=None (unanswered) should NOT silently pass a
    # required check - it's treated the same as "no".
    job_config = make_job_config(requires_driving_licence=True)
    candidate = make_candidate(has_driving_licence=None)
    assert "Missing driving licence" in check_hard_rules(candidate, job_config)


def test_all_three_hard_rules_can_fail_at_once():
    job_config = make_job_config(
        requires_driving_licence=True,
        requires_shift_flexibility=True,
        requires_commute=True,
    )
    candidate = make_candidate(
        has_driving_licence=False,
        willing_to_work_shifts=False,
        can_commute=False,
    )
    issues = check_hard_rules(candidate, job_config)
    assert len(issues) == 3
    assert "Missing driving licence" in issues
    assert "Not willing to work shifts" in issues
    assert "Cannot commute" in issues


def test_candidate_meeting_all_requirements_passes():
    job_config = make_job_config(
        requires_driving_licence=True,
        requires_shift_flexibility=True,
        requires_commute=True,
    )
    candidate = make_candidate(
        has_driving_licence=True,
        willing_to_work_shifts=True,
        can_commute=True,
    )
    assert check_hard_rules(candidate, job_config) == []
