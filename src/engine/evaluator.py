from src.engine.rules import check_hard_rules
from src.engine.scoring import calculate_score
from src.engine.decision import get_decision
from src.engine.summary import generate_summary
from src.models.candidate import Candidate
from src.models.job_config import JobConfig
from src.models.result import EvaluationResult


def evaluate_candidate(candidate: Candidate, job_config: JobConfig) -> EvaluationResult:
    hard_rule_issues = check_hard_rules(candidate, job_config)

    if hard_rule_issues:
        return EvaluationResult(
            candidate_id=candidate.candidate_id,
            job_id=candidate.job_id,
            score=0,
            decision="Reject",
            issues=hard_rule_issues,
            summary=generate_summary(candidate, 0, "Reject", hard_rule_issues),
        )

    score, scoring_issues = calculate_score(candidate, job_config)
    decision = get_decision(score, job_config)
    summary = generate_summary(candidate, score, decision, scoring_issues)

    return EvaluationResult(
        candidate_id=candidate.candidate_id,
        job_id=candidate.job_id,
        score=score,
        decision=decision,
        issues=scoring_issues,
        summary=summary,
    )