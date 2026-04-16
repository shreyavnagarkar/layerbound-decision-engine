# Layerbound Intake Evaluation API

A simple FastAPI-based intake system that evaluates candidate/enquiry data and returns structured outcomes.

## Features

- Rule-based validation (hard requirements)
- Scoring system (0–100)
- Intake status:
  - ready_for_follow_up
  - needs_follow_up
  - low_fit
- Missing information detection
- Suggested next steps
- Recruiter-friendly summary

## Run locally

```bash
PYTHONPATH=. uvicorn src.api:app --reload
