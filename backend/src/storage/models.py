"""SQLAlchemy ORM models. Not imported outside src/storage — see repository.py."""
import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.db import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class JobConfigORM(Base):
    __tablename__ = "job_configs"

    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, default="")

    requires_driving_licence: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_shift_flexibility: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_commute: Mapped[bool] = mapped_column(Boolean, default=False)

    salary_min: Mapped[int] = mapped_column(Integer)
    salary_max: Mapped[int] = mapped_column(Integer)
    max_notice_days: Mapped[int] = mapped_column(Integer)

    score_threshold_submit: Mapped[int] = mapped_column(Integer, default=80)
    score_threshold_review: Mapped[int] = mapped_column(Integer, default=50)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class EvaluationORM(Base):
    """
    One row per /evaluate call: a snapshot of the candidate's answers plus
    the result produced for them. Evaluations are append-only (a re-submit
    creates a new row) so the history stays intact for analysis.
    """

    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    candidate_id: Mapped[str] = mapped_column(String, index=True)
    job_id: Mapped[str] = mapped_column(String, index=True)

    # candidate answers, snapshotted at evaluation time
    has_driving_licence: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    willing_to_work_shifts: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    can_commute: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    expected_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # result
    score: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String, index=True)
    issues_json: Mapped[str] = mapped_column(Text, default="[]")
    summary: Mapped[str] = mapped_column(Text)
    hard_reject: Mapped[bool] = mapped_column(Boolean, default=False)
    score_breakdown_json: Mapped[str] = mapped_column(Text, default="[]")
    missing_info_json: Mapped[str] = mapped_column(Text, default="[]")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
