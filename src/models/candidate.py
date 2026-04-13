from pydantic import BaseModel, Field


class Candidate(BaseModel):
    candidate_id: str
    job_id: str
    has_driving_licence: bool
    willing_to_work_shifts: bool
    can_commute: bool
    expected_salary: int = Field(ge=0)
    notice_period_days: int = Field(ge=0)
    fit_score: int = Field(ge=1, le=10)

