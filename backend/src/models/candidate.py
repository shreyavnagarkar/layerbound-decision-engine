from pydantic import BaseModel, Field
from typing import Optional


class Candidate(BaseModel):
    candidate_id: str
    job_id: str

    has_driving_licence: Optional[bool] = None
    willing_to_work_shifts: Optional[bool] = None
    can_commute: Optional[bool] = None

    expected_salary: Optional[int] = Field(default=None, ge=0)
    notice_period_days: Optional[int] = Field(default=None, ge=0)
    fit_score: Optional[int] = Field(default=None, ge=1, le=10)
