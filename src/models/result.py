from pydantic import BaseModel
from typing import List


class EvaluationResult(BaseModel):
    candidate_id: str
    job_id: str
    score: int
    decision: str
    issues: List[str]
    summary: str