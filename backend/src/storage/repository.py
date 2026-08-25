"""
Storage interface used by the API layer.

Every public method here speaks in Pydantic models (Candidate, JobConfig,
EvaluationResult, EvaluationRecord, DashboardStats, ...) - never SQLAlchemy
objects - on purpose: this is the seam where a future DynamoDB-backed
implementation can be dropped in without touching src/api.py. See the
README's "Swapping storage for DynamoDB" section.
"""
import json
from collections import Counter
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.candidate import Candidate
from src.models.job_config import JobConfig
from src.models.result import EvaluationResult, ScoreBreakdownItem
from src.storage.models import EvaluationORM, JobConfigORM
from src.storage.schemas import (
    DashboardStats,
    DecisionBreakdown,
    EvaluationRecord,
    RejectionReasonCount,
)


class EvaluationRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---- job configs ----

    def upsert_job_config(self, job_config: JobConfig) -> JobConfig:
        existing = self.db.get(JobConfigORM, job_config.job_id)
        if existing is None:
            existing = JobConfigORM(job_id=job_config.job_id)
            self.db.add(existing)

        existing.title = job_config.title
        existing.requires_driving_licence = job_config.requires_driving_licence
        existing.requires_shift_flexibility = job_config.requires_shift_flexibility
        existing.requires_commute = job_config.requires_commute
        existing.salary_min = job_config.salary_min
        existing.salary_max = job_config.salary_max
        existing.max_notice_days = job_config.max_notice_days
        existing.score_threshold_submit = job_config.score_threshold_submit
        existing.score_threshold_review = job_config.score_threshold_review

        self.db.commit()
        self.db.refresh(existing)
        return _job_config_from_orm(existing)

    def get_job_config(self, job_id: str) -> Optional[JobConfig]:
        row = self.db.get(JobConfigORM, job_id)
        return _job_config_from_orm(row) if row else None

    def list_job_configs(self) -> List[JobConfig]:
        rows = self.db.execute(select(JobConfigORM).order_by(JobConfigORM.job_id)).scalars().all()
        return [_job_config_from_orm(row) for row in rows]

    def delete_job_config(self, job_id: str) -> bool:
        row = self.db.get(JobConfigORM, job_id)
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

    # ---- evaluations ----

    def save_evaluation(
        self, candidate: Candidate, result: EvaluationResult, missing_info: List[str]
    ) -> EvaluationRecord:
        row = EvaluationORM(
            candidate_id=candidate.candidate_id,
            job_id=candidate.job_id,
            has_driving_licence=candidate.has_driving_licence,
            willing_to_work_shifts=candidate.willing_to_work_shifts,
            can_commute=candidate.can_commute,
            expected_salary=candidate.expected_salary,
            notice_period_days=candidate.notice_period_days,
            fit_score=candidate.fit_score,
            score=result.score,
            decision=result.decision,
            issues_json=json.dumps(result.issues),
            summary=result.summary,
            hard_reject=result.hard_reject,
            score_breakdown_json=json.dumps([item.model_dump() for item in result.score_breakdown]),
            missing_info_json=json.dumps(missing_info),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return _evaluation_from_orm(row)

    def get_evaluation(self, evaluation_id: int) -> Optional[EvaluationRecord]:
        row = self.db.get(EvaluationORM, evaluation_id)
        return _evaluation_from_orm(row) if row else None

    def list_evaluations(
        self,
        job_id: Optional[str] = None,
        decision: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[EvaluationRecord]:
        stmt = select(EvaluationORM).order_by(EvaluationORM.created_at.desc())
        if job_id:
            stmt = stmt.where(EvaluationORM.job_id == job_id)
        if decision:
            stmt = stmt.where(EvaluationORM.decision == decision)
        stmt = stmt.offset(offset).limit(limit)
        rows = self.db.execute(stmt).scalars().all()
        return [_evaluation_from_orm(row) for row in rows]

    def count_evaluations(self, job_id: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(EvaluationORM)
        if job_id:
            stmt = stmt.where(EvaluationORM.job_id == job_id)
        return self.db.execute(stmt).scalar_one()

    def get_dashboard_stats(self, job_id: Optional[str] = None, recent_limit: int = 10) -> DashboardStats:
        stmt = select(EvaluationORM)
        if job_id:
            stmt = stmt.where(EvaluationORM.job_id == job_id)
        rows = self.db.execute(stmt).scalars().all()

        total = len(rows)
        breakdown = DecisionBreakdown()
        reason_counts = Counter()
        hard_rejects = 0
        score_sum = 0

        for row in rows:
            if row.decision == "Submit":
                breakdown.submit += 1
            elif row.decision == "Review":
                breakdown.review += 1
            elif row.decision == "Reject":
                breakdown.reject += 1
            if row.hard_reject:
                hard_rejects += 1
            score_sum += row.score
            if row.decision == "Reject":
                for reason in json.loads(row.issues_json):
                    reason_counts[reason] += 1

        percent_rejected = (breakdown.reject / total * 100) if total else 0.0
        percent_hard_rejected = (hard_rejects / total * 100) if total else 0.0
        average_score = (score_sum / total) if total else None

        top_reasons = [
            RejectionReasonCount(reason=reason, count=count)
            for reason, count in reason_counts.most_common(10)
        ]

        recent_stmt = select(EvaluationORM).order_by(EvaluationORM.created_at.desc())
        if job_id:
            recent_stmt = recent_stmt.where(EvaluationORM.job_id == job_id)
        recent_stmt = recent_stmt.limit(recent_limit)
        recent_rows = self.db.execute(recent_stmt).scalars().all()

        return DashboardStats(
            total_evaluations=total,
            decision_breakdown=breakdown,
            percent_rejected=round(percent_rejected, 1),
            percent_hard_rejected=round(percent_hard_rejected, 1),
            average_score=round(average_score, 1) if average_score is not None else None,
            top_rejection_reasons=top_reasons,
            recent_evaluations=[_evaluation_from_orm(row) for row in recent_rows],
        )


def _job_config_from_orm(row: JobConfigORM) -> JobConfig:
    return JobConfig(
        job_id=row.job_id,
        title=row.title,
        requires_driving_licence=row.requires_driving_licence,
        requires_shift_flexibility=row.requires_shift_flexibility,
        requires_commute=row.requires_commute,
        salary_min=row.salary_min,
        salary_max=row.salary_max,
        max_notice_days=row.max_notice_days,
        score_threshold_submit=row.score_threshold_submit,
        score_threshold_review=row.score_threshold_review,
    )


def _evaluation_from_orm(row: EvaluationORM) -> EvaluationRecord:
    return EvaluationRecord(
        id=row.id,
        candidate_id=row.candidate_id,
        job_id=row.job_id,
        has_driving_licence=row.has_driving_licence,
        willing_to_work_shifts=row.willing_to_work_shifts,
        can_commute=row.can_commute,
        expected_salary=row.expected_salary,
        notice_period_days=row.notice_period_days,
        fit_score=row.fit_score,
        score=row.score,
        decision=row.decision,
        issues=json.loads(row.issues_json),
        summary=row.summary,
        hard_reject=row.hard_reject,
        score_breakdown=[ScoreBreakdownItem(**item) for item in json.loads(row.score_breakdown_json)],
        missing_info=json.loads(row.missing_info_json),
        created_at=row.created_at,
    )
