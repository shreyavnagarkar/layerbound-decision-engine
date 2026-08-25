"""Small CLI demo of the evaluation engine, independent of the API/DB."""
from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def main():
    candidate = Candidate(
        candidate_id="CAND-001",
        job_id="JOB-001",
        has_driving_licence=True,
        willing_to_work_shifts=True,
        can_commute=True,
        expected_salary=42000,
        notice_period_days=45,
        fit_score=7,
    )

    job_config = JobConfig(
        job_id="JOB-001",
        title="Warehouse Operative",
        requires_driving_licence=True,
        requires_shift_flexibility=True,
        requires_commute=True,
        salary_min=30000,
        salary_max=40000,
        max_notice_days=60,
    )

    result = evaluate_candidate(candidate, job_config)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
