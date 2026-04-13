from fastapi import FastAPI
from src.engine.evaluator import evaluate_candidate
from src.models.candidate import Candidate
from src.models.job_config import JobConfig

app = FastAPI(title="Candidate Evaluation API")


@app.post("/evaluate")
def evaluate(candidate: Candidate, job_config: JobConfig):
    result = evaluate_candidate(candidate, job_config)
    return result.model_dump()