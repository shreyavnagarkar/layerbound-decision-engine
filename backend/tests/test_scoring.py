from src.engine.scoring import calculate_score
from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def make_job_config(**overrides):
    defaults = dict(
        job_id="JOB-001",
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


def test_base_score_with_no_data_is_fifty():
    job_config = make_job_config()
    candidate = make_candidate()
    score, issues, breakdown = calculate_score(candidate, job_config)
    assert score == 50
    assert "Expected salary missing" in issues
    assert "Notice period missing" in issues
    assert "Fit score missing" in issues
    assert breakdown[0].label == "Base score"


def test_salary_within_range_adds_twenty():
    job_config = make_job_config()
    candidate = make_candidate(expected_salary=35000)
    score, issues, _ = calculate_score(candidate, job_config)
    assert score == 70  # 50 + 20
    assert not any("Salary" in i for i in issues)


def test_salary_slightly_above_range_adds_five_and_flags():
    job_config = make_job_config()
    candidate = make_candidate(expected_salary=42000)  # max=40000, +5000 buffer
    score, issues, _ = calculate_score(candidate, job_config)
    assert score == 55  # 50 + 5
    assert "Salary slightly above range" in issues


def test_salary_far_above_range_subtracts_fifteen():
    job_config = make_job_config()
    candidate = make_candidate(expected_salary=50000)  # > max + 5000
    score, issues, _ = calculate_score(candidate, job_config)
    assert score == 35  # 50 - 15
    assert "Salary significantly above range" in issues


def test_notice_period_short_adds_fifteen():
    job_config = make_job_config()
    candidate = make_candidate(notice_period_days=14)
    score, _, _ = calculate_score(candidate, job_config)
    assert score == 65  # 50 + 15


def test_notice_period_over_job_max_subtracts_ten():
    job_config = make_job_config(max_notice_days=60)
    candidate = make_candidate(notice_period_days=90)
    score, issues, _ = calculate_score(candidate, job_config)
    assert score == 40  # 50 - 10
    assert "Notice period longer than preferred" in issues


def test_fit_score_high_adds_fifteen():
    job_config = make_job_config()
    candidate = make_candidate(fit_score=9)
    score, _, _ = calculate_score(candidate, job_config)
    assert score == 65


def test_fit_score_low_subtracts_ten():
    job_config = make_job_config()
    candidate = make_candidate(fit_score=2)
    score, issues, _ = calculate_score(candidate, job_config)
    assert score == 40
    assert "Low general fit" in issues


def test_score_is_clamped_to_zero_and_hundred():
    job_config = make_job_config()
    # everything maxed out negatively
    candidate = make_candidate(expected_salary=100000, notice_period_days=200, fit_score=1)
    score, _, _ = calculate_score(candidate, job_config)
    assert 0 <= score <= 100

    # everything maxed out positively
    candidate = make_candidate(expected_salary=35000, notice_period_days=10, fit_score=10)
    score, _, _ = calculate_score(candidate, job_config)
    assert score == 100  # 50 + 20 + 15 + 15


def test_breakdown_points_sum_to_final_score_before_clamping():
    job_config = make_job_config()
    candidate = make_candidate(expected_salary=35000, notice_period_days=10, fit_score=9)
    score, _, breakdown = calculate_score(candidate, job_config)
    assert sum(item.points for item in breakdown) == score
