import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig
from src.storage.db import get_db, init_db
from src.storage.repository import EvaluationRepository
from src.storage.schemas import DashboardStats, EvaluationRecord


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Layerbound Intake Evaluation API", lifespan=lifespan)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
        frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    candidate: Candidate
    # Optional: if provided, this job config is created/updated (upserted)
    # before evaluating. If omitted, the job config already stored for
    # candidate.job_id is used - lets a recruiter set the job up once via
    # POST /jobs and then submit many candidates against just their job_id.
    job_config: Optional[JobConfig] = None


class EvaluateResponse(BaseModel):
    id: int
    candidate_id: str
    job_id: str
    score: int
    decision: str
    issues: List[str]
    summary: str
    hard_reject: bool
    score_breakdown: List[dict]
    missing_info: List[str]
    next_steps: List[str]


NEXT_STEPS = {
    "Submit": ["Schedule interview"],
    "Review": ["Review profile", "Clarify concerns"],
    "Reject": ["Reject or archive"],
}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/jobs", response_model=JobConfig)
def upsert_job(job_config: JobConfig, db: Session = Depends(get_db)):
    """Create or update a job's evaluation config (requirements, salary band, thresholds)."""
    repo = EvaluationRepository(db)
    return repo.upsert_job_config(job_config)


@app.get("/jobs", response_model=List[JobConfig])
def list_jobs(db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)
    return repo.list_job_configs()


@app.get("/jobs/{job_id}", response_model=JobConfig)
def get_job(job_id: str, db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)
    job_config = repo.get_job_config(job_id)
    if job_config is None:
        raise HTTPException(status_code=404, detail=f"No job config found for job_id '{job_id}'")
    return job_config


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)
    if not repo.delete_job_config(job_id):
        raise HTTPException(status_code=404, detail=f"No job config found for job_id '{job_id}'")
    return {"status": "deleted", "job_id": job_id}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest, db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)

    if request.job_config is not None:
        if request.job_config.job_id != request.candidate.job_id:
            raise HTTPException(
                status_code=400,
                detail="candidate.job_id and job_config.job_id must match",
            )
        job_config = repo.upsert_job_config(request.job_config)
    else:
        job_config = repo.get_job_config(request.candidate.job_id)
        if job_config is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No job config found for job_id '{request.candidate.job_id}'. "
                    "Create one first via POST /jobs, or include job_config in this request."
                ),
            )

    result = evaluate_candidate(request.candidate, job_config)

    missing_info = []
    if request.candidate.expected_salary is None:
        missing_info.append("expected_salary")
    if request.candidate.notice_period_days is None:
        missing_info.append("notice_period_days")
    if request.candidate.fit_score is None:
        missing_info.append("fit_score")

    record = repo.save_evaluation(request.candidate, result, missing_info)

    return EvaluateResponse(
        id=record.id,
        candidate_id=result.candidate_id,
        job_id=result.job_id,
        score=result.score,
        decision=result.decision,
        issues=result.issues,
        summary=result.summary,
        hard_reject=result.hard_reject,
        score_breakdown=[item.model_dump() for item in result.score_breakdown],
        missing_info=missing_info,
        next_steps=NEXT_STEPS[result.decision],
    )


@app.get("/evaluations", response_model=List[EvaluationRecord])
def list_evaluations(
    job_id: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    repo = EvaluationRepository(db)
    return repo.list_evaluations(job_id=job_id, decision=decision, limit=limit, offset=offset)


@app.get("/evaluations/{evaluation_id}", response_model=EvaluationRecord)
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)
    record = repo.get_evaluation(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No evaluation found with id {evaluation_id}")
    return record


@app.get("/dashboard", response_model=DashboardStats)
def dashboard(job_id: Optional[str] = None, db: Session = Depends(get_db)):
    repo = EvaluationRepository(db)
    return repo.get_dashboard_stats(job_id=job_id)
