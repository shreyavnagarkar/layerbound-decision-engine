from src.models.candidate import Candidate


def generate_summary(candidate: Candidate, score: int, decision: str, issues: list[str]) -> str:
    if decision == "Reject" and issues:
        return (
            f"Candidate is not suitable at this stage. "
            f"Key concerns: {', '.join(issues)}. "
            f"Final score is {score}."
        )

    if issues:
        return (
            f"Candidate passed mandatory checks and scored {score}. "
            f"There are some concerns: {', '.join(issues)}. "
            f"Recommended decision: {decision}."
        )

    return (
        f"Candidate passed mandatory checks with a strong overall profile. "
        f"Final score is {score}. "
        f"Recommended decision: {decision}."
    )
