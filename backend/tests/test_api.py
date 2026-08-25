def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_fetch_job(client, sample_job_config):
    response = client.post("/jobs", json=sample_job_config.model_dump())
    assert response.status_code == 200
    assert response.json()["job_id"] == "JOB-001"

    response = client.get("/jobs/JOB-001")
    assert response.status_code == 200
    assert response.json()["salary_max"] == 40000


def test_get_unknown_job_returns_404(client):
    response = client.get("/jobs/does-not-exist")
    assert response.status_code == 404


def test_list_jobs(client, sample_job_config):
    client.post("/jobs", json=sample_job_config.model_dump())
    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_evaluate_with_inline_job_config_creates_job_and_persists_result(
    client, sample_candidate, sample_job_config
):
    response = client.post(
        "/evaluate",
        json={
            "candidate": sample_candidate.model_dump(),
            "job_config": sample_job_config.model_dump(),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == "CAND-001"
    assert body["decision"] in ("Submit", "Review", "Reject")
    assert "id" in body

    # the job config should now exist on its own
    assert client.get("/jobs/JOB-001").status_code == 200

    # the evaluation should be retrievable
    fetched = client.get(f"/evaluations/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["candidate_id"] == "CAND-001"


def test_evaluate_without_job_config_uses_previously_stored_one(
    client, sample_candidate, sample_job_config
):
    client.post("/jobs", json=sample_job_config.model_dump())

    response = client.post("/evaluate", json={"candidate": sample_candidate.model_dump()})
    assert response.status_code == 200


def test_evaluate_without_job_config_and_no_stored_job_returns_404(client, sample_candidate):
    response = client.post("/evaluate", json={"candidate": sample_candidate.model_dump()})
    assert response.status_code == 404


def test_evaluate_mismatched_job_ids_returns_400(client, sample_candidate, sample_job_config):
    other_job = sample_job_config.model_dump()
    other_job["job_id"] = "JOB-999"
    response = client.post(
        "/evaluate",
        json={"candidate": sample_candidate.model_dump(), "job_config": other_job},
    )
    assert response.status_code == 400


def test_hard_reject_is_persisted_and_flagged(client, sample_job_config):
    candidate = {
        "candidate_id": "CAND-002",
        "job_id": "JOB-001",
        "has_driving_licence": False,
        "willing_to_work_shifts": True,
        "can_commute": True,
    }
    response = client.post(
        "/evaluate",
        json={"candidate": candidate, "job_config": sample_job_config.model_dump()},
    )
    body = response.json()
    assert body["decision"] == "Reject"
    assert body["hard_reject"] is True
    assert body["score"] == 0


def test_missing_info_reported(client, sample_job_config):
    candidate = {
        "candidate_id": "CAND-003",
        "job_id": "JOB-001",
        "has_driving_licence": True,
        "willing_to_work_shifts": True,
        "can_commute": True,
    }
    response = client.post(
        "/evaluate",
        json={"candidate": candidate, "job_config": sample_job_config.model_dump()},
    )
    body = response.json()
    assert set(body["missing_info"]) == {"expected_salary", "notice_period_days", "fit_score"}


def test_list_evaluations_filters_by_job_id_and_decision(client, sample_job_config):
    client.post("/jobs", json=sample_job_config.model_dump())

    strong = {
        "candidate_id": "CAND-STRONG",
        "job_id": "JOB-001",
        "has_driving_licence": True,
        "willing_to_work_shifts": True,
        "can_commute": True,
        "expected_salary": 35000,
        "notice_period_days": 10,
        "fit_score": 10,
    }
    client.post("/evaluate", json={"candidate": strong})

    hard_reject = {
        "candidate_id": "CAND-REJECT",
        "job_id": "JOB-001",
        "has_driving_licence": False,
        "willing_to_work_shifts": True,
        "can_commute": True,
    }
    client.post("/evaluate", json={"candidate": hard_reject})

    all_for_job = client.get("/evaluations", params={"job_id": "JOB-001"}).json()
    assert len(all_for_job) == 2

    only_submit = client.get(
        "/evaluations", params={"job_id": "JOB-001", "decision": "Submit"}
    ).json()
    assert len(only_submit) == 1
    assert only_submit[0]["candidate_id"] == "CAND-STRONG"


def test_dashboard_aggregates_correctly(client, sample_job_config):
    client.post("/jobs", json=sample_job_config.model_dump())

    # one clean submit
    client.post(
        "/evaluate",
        json={
            "candidate": {
                "candidate_id": "CAND-A",
                "job_id": "JOB-001",
                "has_driving_licence": True,
                "willing_to_work_shifts": True,
                "can_commute": True,
                "expected_salary": 35000,
                "notice_period_days": 10,
                "fit_score": 10,
            }
        },
    )

    # two hard rejects for the same reason
    for cid in ("CAND-B", "CAND-C"):
        client.post(
            "/evaluate",
            json={
                "candidate": {
                    "candidate_id": cid,
                    "job_id": "JOB-001",
                    "has_driving_licence": False,
                    "willing_to_work_shifts": True,
                    "can_commute": True,
                }
            },
        )

    response = client.get("/dashboard", params={"job_id": "JOB-001"})
    assert response.status_code == 200
    stats = response.json()

    assert stats["total_evaluations"] == 3
    assert stats["decision_breakdown"]["submit"] == 1
    assert stats["decision_breakdown"]["reject"] == 2
    assert stats["percent_rejected"] == round(2 / 3 * 100, 1)
    assert stats["percent_hard_rejected"] == round(2 / 3 * 100, 1)
    assert stats["top_rejection_reasons"][0]["reason"] == "Missing driving licence"
    assert stats["top_rejection_reasons"][0]["count"] == 2
    assert len(stats["recent_evaluations"]) == 3


def test_dashboard_with_no_evaluations_does_not_error(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_evaluations"] == 0
    assert stats["average_score"] is None
    assert stats["percent_rejected"] == 0
