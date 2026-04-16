from fastapi import FastAPI
from pydantic import BaseModel

from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig

app = FastAPI()


class IntakeRequest(BaseModel):
    candidate: Candidate
    job_config: JobConfig


@app.post("/evaluate")
def evaluate(request: IntakeRequest):
    result = evaluate_candidate(request.candidate, request.job_config)

    # Map to intake API language
    if result.decision == "Submit":
        status = "ready_for_follow_up"
        next_steps = ["Schedule interview"]
    elif result.decision == "Review":
        status = "needs_follow_up"
        next_steps = ["Review profile", "Clarify concerns"]
    else:
        status = "low_fit"
        next_steps = ["Reject or archive"]

    # Detect missing info
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