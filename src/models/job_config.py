from pydantic import BaseModel, Field


class JobConfig(BaseModel):
    job_id: str
    requires_driving_licence: bool = False
    requires_shift_flexibility: bool = False
    requires_commute: bool = False
    salary_min: int = Field(ge=0)
    salary_max: int = Field(ge=0)
    max_notice_days: int = Field(ge=0)

    score_threshold_submit: int = 80
    score_threshold_review: int = 50
