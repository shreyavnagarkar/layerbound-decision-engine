from src.models.job_config import JobConfig


def get_decision(score: int, job_config: JobConfig) -> str:
    if score >= job_config.score_threshold_submit:
        return "Submit"
    if score >= job_config.score_threshold_review:
        return "Review"
    return "Reject"
