"""
Pydantic shapes returned by the repository layer. Keeping these separate
from the ORM models is what lets api.py (and any future caller) stay
ignorant of SQLAlchemy entirely.
"""
import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.models.result import ScoreBreakdownItem


class EvaluationRecord(BaseModel):
    id: int
    candidate_id: str
    job_id: str

    has_driving_licence: Optional[bool] = None
    willing_to_work_shifts: Optional[bool] = None
    can_commute: Optional[bool] = None
    expected_salary: Optional[int] = None
    notice_period_days: Optional[int] = None
    fit_score: Optional[int] = None

    score: int
    decision: str
    issues: List[str]
    summary: str
    hard_reject: bool
    score_breakdown: List[ScoreBreakdownItem]
    missing_info: List[str]

    created_at: datetime.datetime


class DecisionBreakdown(BaseModel):
    submit: int = 0
    review: int = 0
    reject: int = 0


class RejectionReasonCount(BaseModel):
    reason: str
    count: int


class DashboardStats(BaseModel):
    total_evaluations: int
    decision_breakdown: DecisionBreakdown
    percent_rejected: float
    percent_hard_rejected: float
    average_score: Optional[float]
    top_rejection_reasons: List[RejectionReasonCount]
    recent_evaluations: List[EvaluationRecord]
