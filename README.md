# Layerbound Intake Evaluation API

A simple full-stack intake demo that evaluates candidate or enquiry data and returns a structured result.

## What it does

- accepts intake data from a small React frontend
- sends the data to a FastAPI backend
- evaluates the input using simple rule-based logic
- returns:
  - status
  - score
  - issues
  - missing information
  - next steps
  - summary

## Tech stack

- Python
- FastAPI
- React
- Vite

## API statuses

The API returns one of these statuses:

- `ready_for_follow_up`
- `needs_follow_up`
- `low_fit`

## Run locally

### 1. Start the backend

From the project root:

```bash
source venv/bin/activate
PYTHONPATH=. uvicorn src.api:app --reload
