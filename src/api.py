from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig

app = FastAPI(title="Layerbound Intake Evaluation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IntakeRequest(BaseModel):
    candidate: Candidate
    job_config: JobConfig


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(request: IntakeRequest):
    result = evaluate_candidate(request.candidate, request.job_config)

    if result.decision == "Submit":
        status = "ready_for_follow_up"
        next_steps = ["Schedule interview"]
    elif result.decision == "Review":
        status = "needs_follow_up"
        next_steps = ["Review profile", "Clarify concerns"]
    else:
        status = "low_fit"
        next_steps = ["Reject or archive"]

    missing_info = []
    if request.candidate.expected_salary is None:
        missing_info.append("expected_salary")
    if request.candidate.notice_period_days is None:
        missing_info.append("notice_period_days")
    if request.candidate.fit_score is None:
        missing_info.append("fit_score")

    return {
        "candidate_id": result.candidate_id,
        "job_id": result.job_id,
        "status": status,
        "score": result.score,
        "issues": result.issues,
        "missing_info": missing_info,
        "next_steps": next_steps,
        "summary": result.summary,
    }