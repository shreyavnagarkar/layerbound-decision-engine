from src.models.candidate import Candidate
from src.models.job_config import JobConfig


def check_hard_rules(candidate: Candidate, job_config: JobConfig) -> list[str]:
    """Automatic-reject checks. Any item returned here short-circuits scoring."""
    issues = []

    if job_config.requires_driving_licence and not candidate.has_driving_licence:
        issues.append("Missing driving licence")

    if job_config.requires_shift_flexibility and not candidate.willing_to_work_shifts:
        issues.append("Not willing to work shifts")

    if job_config.requires_commute and not candidate.can_commute:
        issues.append("Cannot commute")

    return issues
