from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def calculate_score(candidate: Candidate, job_config: JobConfig) -> tuple[int, list[str]]:
    score = 50
    issues = []

    if candidate.expected_salary is not None:
        if job_config.salary_min <= candidate.expected_salary <= job_config.salary_max:
            score += 20
        elif candidate.expected_salary <= job_config.salary_max + 5000:
            score += 5
            issues.append("Salary slightly above range")
        else:
            score -= 15
            issues.append("Salary significantly above range")

    if candidate.notice_period_days is not None:
        if candidate.notice_period_days <= 30:
            score += 15
        elif candidate.notice_period_days <= job_config.max_notice_days:
            score += 5
        else:
            score -= 10
            issues.append("Notice period longer than preferred")

    if candidate.fit_score is not None:
        if candidate.fit_score >= 8:
            score += 15
        elif candidate.fit_score >= 5:
            score += 5
        else:
            score -= 10
            issues.append("Low general fit")

    score = max(0, min(100, score))
    return score, issues