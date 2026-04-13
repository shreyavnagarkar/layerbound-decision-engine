from pydantic import BaseModel


class EvaluationResult(BaseModel):
    candidate_id: str
    job_id: str
    score: int
    decision: str
    issues: list[str]
    summary: str
