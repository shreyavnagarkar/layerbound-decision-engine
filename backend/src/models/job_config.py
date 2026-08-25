from pydantic import BaseModel, Field, model_validator


class JobConfig(BaseModel):
    job_id: str
    title: str = ""

    requires_driving_licence: bool = False
    requires_shift_flexibility: bool = False
    requires_commute: bool = False

    salary_min: int = Field(ge=0)
    salary_max: int = Field(ge=0)
    max_notice_days: int = Field(ge=0)

    score_threshold_submit: int = 80
    score_threshold_review: int = 50

    @model_validator(mode="after")
    def _validate_ranges(self) -> "JobConfig":
        if self.salary_max < self.salary_min:
            raise ValueError("salary_max must be greater than or equal to salary_min")
        if not (0 <= self.score_threshold_review <= self.score_threshold_submit <= 100):
            raise ValueError(
                "thresholds must satisfy 0 <= score_threshold_review <= "
                "score_threshold_submit <= 100"
            )
        return self
