@app.post("/evaluate")
def evaluate(request: IntakeRequest):
    result = evaluate_candidate(request.candidate, request.job_config)

    if result.decision == "Submit":
        next_steps = ["Schedule interview"]
    elif result.decision == "Review":
        next_steps = ["Review profile", "Clarify concerns"]
    else:
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
        "score": result.score,
        "decision": result.decision,
        "issues": result.issues,
        "summary": result.summary,
        "hard_reject": result.hard_reject,
        "score_breakdown": [item.model_dump() for item in result.score_breakdown],
        "missing_info": missing_info,
        "next_steps": next_steps,
    }