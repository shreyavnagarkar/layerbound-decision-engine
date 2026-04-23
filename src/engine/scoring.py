from src.models.candidate import Candidate
from src.models.job_config import JobConfig
from src.models.result import ScoreBreakdownItem


def calculate_score(
    candidate: Candidate, job_config: JobConfig
) -> tuple[int, list[str], list[ScoreBreakdownItem]]:
    score = 50
    issues: list[str] = []
    breakdown: list[ScoreBreakdownItem] = [
        ScoreBreakdownItem(label="Base score", points=50, note="Starting point for all candidates")
    ]

    if candidate.expected_salary is not None:
        if job_config.salary_min <= candidate.expected_salary <= job_config.salary_max:
            score += 20
            breakdown.append(
                ScoreBreakdownItem(
                    label="Salary alignment",
                    points=20,
                    note="Expected salary is within the target range",
                )
            )
        elif candidate.expected_salary <= job_config.salary_max + 5000:
            score += 5
            issues.append("Salary slightly above range")
            breakdown.append(
                ScoreBreakdownItem(
                    label="Salary alignment",
                    points=5,
                    note="Expected salary is slightly above the target range",
                )
            )
        else:
            score -= 15
            issues.append("Salary significantly above range")
            breakdown.append(
                ScoreBreakdownItem(
                    label="Salary alignment",
                    points=-15,
                    note="Expected salary is significantly above the target range",
                )
            )
    else:
        issues.append("Expected salary missing")
        breakdown.append(
            ScoreBreakdownItem(
                label="Salary alignment",
                points=0,
                note="Expected salary was not provided",
            )
        )

    if candidate.notice_period_days is not None:
        if candidate.notice_period_days <= 30:
            score += 15
            breakdown.append(
                ScoreBreakdownItem(
                    label="Notice period",
                    points=15,
                    note="Notice period is within the preferred range",
                )
            )
        elif candidate.notice_period_days <= job_config.max_notice_days:
            score += 5
            issues.append("Notice period acceptable but not ideal")
            breakdown.append(
                ScoreBreakdownItem(
                    label="Notice period",
                    points=5,
                    note="Notice period is acceptable but longer than preferred",
                )
            )
        else:
            score -= 10
            issues.append("Notice period longer than preferred")
            breakdown.append(
                ScoreBreakdownItem(
                    label="Notice period",
                    points=-10,
                    note="Notice period exceeds the preferred maximum",
                )
            )
    else:
        issues.append("Notice period missing")
        breakdown.append(
            ScoreBreakdownItem(
                label="Notice period",
                points=0,
                note="Notice period was not provided",
            )
        )

    if candidate.fit_score is not None:
        if candidate.fit_score >= 8:
            score += 15
            breakdown.append(
                ScoreBreakdownItem(
                    label="General fit",
                    points=15,
                    note="Strong overall fit assessment",
                )
            )
        elif candidate.fit_score >= 5:
            score += 5
            breakdown.append(
                ScoreBreakdownItem(
                    label="General fit",
                    points=5,
                    note="Moderate overall fit assessment",
                )
            )
        else:
            score -= 10
            issues.append("Low general fit")
            breakdown.append(
                ScoreBreakdownItem(
                    label="General fit",
                    points=-10,
                    note="Low overall fit assessment",
                )
            )
    else:
        issues.append("Fit score missing")
        breakdown.append(
            ScoreBreakdownItem(
                label="General fit",
                points=0,
                note="Fit score was not provided",
            )
        )

    score = max(0, min(100, score))
    return score, issues, breakdown