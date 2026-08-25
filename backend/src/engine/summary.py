from src.models.candidate import Candidate


def generate_summary(candidate: Candidate, score: int, decision: str, issues: list[str]) -> str:
    if decision == "Reject":
        if issues:
            return (
                f"Candidate is not recommended for submission. "
                f"Key issues: {', '.join(issues)}. "
                f"Final score: {score}."
            )
        return (
            f"Candidate is not recommended for submission. "
            f"Final score: {score}."
        )

    if decision == "Review":
        if issues:
            return (
                f"Candidate passed the mandatory checks but needs recruiter review. "
                f"Key issues: {', '.join(issues)}. "
                f"Final score: {score}."
            )
        return (
            f"Candidate passed the mandatory checks and may be worth reviewing further. "
            f"Final score: {score}."
        )

    return (
        f"Candidate passed the mandatory checks and shows strong overall alignment with the role. "
        f"No major issues were identified. "
        f"Final score: {score}."
    )
