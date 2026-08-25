from pydantic import BaseModel
from typing import List, Literal, Optional


class ScoreBreakdownItem(BaseModel):
    label: str
    points: int
    note: Optional[str] = None


class EvaluationResult(BaseModel):
    candidate_id: str
    job_id: str
    score: int
    decision: Literal["Submit", "Review", "Reject"]
    issues: List[str]
    summary: str
    hard_reject: bool = False
    score_breakdown: List[ScoreBreakdownItem] = []
