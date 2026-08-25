# Layerbound Intake Evaluation

Takes candidate intake responses, runs them through hard-rule checks and a
points-based scoring model, and returns a score, a Submit / Review / Reject
decision, flagged issues, and a recruiter-readable summary — plus a
dashboard of trends across everyone evaluated so far.

This is the finished version of the brief Amitesh sent on 22 March: hard
rules → scoring → decision → summary, backed by storage, wrapped in an API,
with a UI on top for both submitting candidates and viewing results.

## Approach

The original evaluation engine (rules → scoring → decision → summary,
composed in `evaluator.py`) was already well-factored and stayed almost
untouched — small, single-purpose functions, easy to test in isolation.
Three real bugs were fixed there (see **Bugs fixed**). Everything else —
storage, the rest of the API, the dashboard, and the frontend — was built
on top of that engine rather than around it, so the core logic stays the
easiest thing in the codebase to read and trust.

The engine is deliberately kept ignorant of HTTP and the database:
`evaluate_candidate(candidate, job_config)` takes and returns plain
Pydantic models. `src/api.py` is the only thing that knows about HTTP
status codes, and `src/storage/repository.py` is the only thing that knows
about SQL. That separation is what makes each layer independently
testable, and it's the seam layerbound's team can cut along if they want
to lift just the engine into their own Lambda.

## What's in this repo

```
backend/
  src/
    models/       Candidate, JobConfig, EvaluationResult - the shared vocabulary
    engine/       rules -> scoring -> decision -> summary -> evaluator
    storage/      SQLAlchemy models, repository (the DB-agnostic interface), schemas
    api.py        FastAPI app: /jobs, /evaluate, /evaluations, /dashboard
    main.py       CLI demo of the engine, no DB/API involved
  tests/          pytest: engine unit tests + API integration tests
frontend/
  src/
    components/   JobForm, CandidateForm, ResultCard, Dashboard
    api/client.js Thin fetch wrapper around the backend
```

## Running it locally

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload
```

The API listens on `http://localhost:8000` and creates `layerbound_intake.db`
(a SQLite file) next to wherever you run it from on first start — no
migration step needed for this MVP. Interactive API docs are at
`http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens on `http://localhost:5173` and talks to the API at
`http://localhost:8000` by default. Copy `.env.example` to `.env` to point
it elsewhere.

### Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

**A note on what's actually been run:** the 24 engine unit tests
(`test_rules.py`, `test_scoring.py`, `test_decision.py`, `test_evaluator.py`)
were executed and pass — they only need Pydantic, which was available in
the sandbox this was built in. The API integration tests
(`test_api.py`, needs FastAPI + SQLAlchemy) and the frontend build/lint
(needs npm) could **not** be executed in that sandbox — outbound access to
PyPI and the npm registry was blocked there (org network policy, not a
project issue). Both were checked as far as the sandbox allowed instead:
every backend file byte-compiles cleanly, and the entire frontend bundles
with esbuild (using the React 19 packages that happened to be available
globally) with all imports resolving and no syntax errors. Please run
`pytest` and `npm run build && npm run lint` yourself before this goes
anywhere near production — that's a real gap in verification, not a
formality.

## Bugs fixed in the handed-off engine code

Three bugs in the original `evaluator.py` would have made `/evaluate`
crash or silently return wrong data:

1. **Unpacking mismatch.** `calculate_score` returns `(score, issues,
   breakdown)` — three values — but `evaluator.py` only unpacked two
   (`score, scoring_issues = calculate_score(...)`). This raised
   `ValueError: too many values to unpack` on every non-hard-reject
   evaluation. Fixed by unpacking all three and passing `breakdown`
   through to the result.
2. **`hard_reject` never set.** `EvaluationResult.hard_reject` defaults to
   `False` and the hard-reject branch never overrode it, so a candidate
   who failed a mandatory check (e.g. no driving licence) would report
   `hard_reject: false` in the API response — the one flag a recruiter
   would rely on to tell "auto-rejected" apart from "scored 0" was wrong.
3. **Score breakdown silently dropped.** Even once the unpacking was
   fixed, `breakdown` was never attached to the returned
   `EvaluationResult`, so the per-factor point breakdown the frontend
   (and `api.py`'s `score_breakdown` field) depends on would always come
   back empty for scored candidates.

All three are covered by `tests/test_evaluator.py`.

## Assumptions made (call these out, per the brief)

- **An unanswered mandatory field fails that check.** If a job requires a
  driving licence and the candidate's answer is blank/unspecified, that's
  treated the same as "no licence" — not skipped, not assumed favourable.
  This was already the original code's behaviour; I kept it and wrote a
  test for it (`test_unanswered_field_treated_as_failing_a_required_check`)
  because it's easy to overlook and worth Amitesh confirming is the
  intended behaviour, rather than "ask the candidate again."
- **Job configs are set up once, then referenced by ID.** The original
  API required the full `JobConfig` on every `/evaluate` call. That's fine
  for a one-off script but awkward for a recruiter submitting many
  candidates against the same role, and it means the job's salary band and
  thresholds live wherever the caller happens to keep them rather than in
  one place you can audit. `POST /jobs` now creates/updates a job once;
  `/evaluate` looks it up by `job_id` if no inline `job_config` is given
  (and still accepts one inline, upserting it, for backward compatibility
  and one-off scripting).
  - **Ask Amitesh:** does layerbound already have a place job requirements
    live (an existing "role" or "requisition" concept), or is this the
    first structured home for them?
- **Evaluations are append-only.** Re-evaluating a candidate creates a new
  row rather than overwriting the previous one, so the dashboard reflects
  full history (e.g. "we re-reviewed and their score improved") rather
  than just the latest state. If layerbound wants "one current result per
  candidate" instead, that's a straightforward change to
  `save_evaluation`.
- **"Most common rejection reasons" counts only `Reject`-decision issues**
  (hard-rule failures and scored rejects), not the softer issues attached
  to `Review` candidates (e.g. "salary slightly above range"). Felt like
  the more useful number for "why are we losing people," but it's a
  judgement call — `Review` issues are still visible per-candidate in
  `/evaluations`, just not aggregated on the dashboard.
- **SQLite for now, by design** — see below.
- **No auth.** Nothing in this repo checks who's calling. Fine for local
  dev and for layerbound to wrap in their own Lambda authorizer /ap
  gateway auth, but worth flagging since it's not mentioned anywhere else
  in this README.

## Swapping storage for DynamoDB

Every storage-facing method on `EvaluationRepository`
(`src/storage/repository.py`) takes and returns plain Pydantic models
(`JobConfig`, `Candidate`, `EvaluationResult`, `EvaluationRecord`,
`DashboardStats`) — never a SQLAlchemy object. `src/api.py` only ever
talks to that interface. That's the seam: a `DynamoEvaluationRepository`
implementing the same method signatures (`upsert_job_config`,
`get_job_config`, `save_evaluation`, `list_evaluations`,
`get_dashboard_stats`, ...) against `boto3` instead of SQLAlchemy can be
swapped in via `Depends(get_db)` → `Depends(get_repository)` without
touching a single route in `api.py`. The one piece worth planning for
ahead of time: `get_dashboard_stats` currently scans and aggregates
in Python, which is trivial on SQLite but won't scale on DynamoDB without
either a `Scan` (fine at small volume, not at large) or precomputed
counters updated on write (a DynamoDB-idiomatic approach — worth doing if
volume grows past a few thousand evaluations).

SQLite was the pragmatic choice for this stage per the brief ("focus on
core logic first") — it needs no setup, the schema is simple, and the
repository interface means the real storage decision isn't blocking
anything else.

## Handoff notes for layerbound (AWS/Lambda/API Gateway/DynamoDB)

I don't have access to layerbound's repo or `deploy.yaml`, so I haven't
guessed at their Terraform or written a Lambda handler against
infrastructure I can't see or test against — that felt likely to be wrong
in some Layerbound-specific way and more work for their team to unwind
than to write themselves. What's here instead is built to make that step
easy:

- `src/api.py` is a standard FastAPI app with no dependency on how it's
  hosted — it runs today under `uvicorn` and would run under Lambda via an
  adapter like [Mangum](https://mangum.io/) with a couple of lines added
  around the existing `app` object, no route changes needed.
- The storage interface (above) is the seam for DynamoDB.
- Config is read from environment variables (`DATABASE_URL`,
  `FRONTEND_URL`) rather than hardcoded, so it drops into Lambda env vars
  or Terraform-injected config the same way.
- Nothing here assumes a long-running process — no in-memory caches or
  background threads — so it's Lambda-cold-start-friendly as-is.

## API reference

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| POST | `/jobs` | Create/update a job's requirements, salary band, and thresholds |
| GET | `/jobs` | List all job configs |
| GET | `/jobs/{job_id}` | Fetch one job config |
| DELETE | `/jobs/{job_id}` | Remove a job config |
| POST | `/evaluate` | Evaluate a candidate (looks up the stored job config by `job_id`, or upserts one if `job_config` is included in the request) |
| GET | `/evaluations` | List past evaluations, filterable by `job_id` / `decision` |
| GET | `/evaluations/{id}` | Fetch one evaluation |
| GET | `/dashboard` | Aggregate stats: totals, % rejected, average score, top rejection reasons, recent evaluations — optionally filtered by `job_id` |

Full interactive docs (request/response shapes, try-it-out) are at
`/docs` once the backend is running.

## What I'd improve next

- **Auth** on the API before it's anywhere near real candidate data.
- **Pagination** on `GET /jobs` (fine at current scale, not at hundreds of
  roles).
- **Editable score weights per job**, not just thresholds — right now the
  point values in `scoring.py` (e.g. "+20 for salary in range") are global
  constants. If different roles should weight salary vs. notice period vs.
  fit differently, that's a `JobConfig` extension, not a rewrite.
- **A confirmation step before overwriting a job config** — `POST /jobs`
  silently upserts, which is convenient for scripting but means a typo'd
  `job_id` on a new job can silently clobber an existing one.

## Questions for Amitesh

1. Is "most common rejection reasons" meant to include `Review`-stage
   issues too, or just hard rejects and scored rejects (see
   **Assumptions**)?
2. Should re-evaluating the same candidate create a new record (current
   behaviour) or update their existing one?
3. Does layerbound have an existing place where job/role requirements
   live, or is `POST /jobs` here the first structured version of that?
4. Any sense yet of expected volume (candidates/day)? Mostly affects how
   soon the DynamoDB dashboard-aggregation question above matters.
