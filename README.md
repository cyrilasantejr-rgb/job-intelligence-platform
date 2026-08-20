# AI Job Intelligence & Application Tracker

An end-to-end platform for collecting internship/new-grad job postings, matching them
against a resume, and tracking applications through a full communication timeline.

This is a portfolio project built in phases. See `docs/architecture.md` (added later)
for the full design. This README covers local setup for **Phase 0**.

## Stack (Phase 0)

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL
- **Infra:** Docker, Docker Compose

Frontend, ingestion pipelines, Airflow, dbt, and AWS are added in later phases.

## Prerequisites

- Docker + Docker Compose installed
- Nothing else — everything runs in containers

## Setup

1. Copy the environment file and adjust if needed:

   ```bash
   cp .env.example .env
   ```

2. Build and start the stack:

   ```bash
   docker compose up --build
   ```

3. In a second terminal, run the initial database migration:

   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. Confirm the API is up:

   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:

   ```json
   {"status": "ok"}
   ```

5. Interactive API docs are available at:

   ```
   http://localhost:8000/docs
   ```

## Running tests

```bash
docker compose exec backend pytest
```

## Project structure

```
job-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── api/routes/    # FastAPI routers
│   │   ├── core/          # config, logging
│   │   ├── db/            # session/engine setup
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── services/      # business logic
│   │   └── main.py        # app entrypoint
│   ├── alembic/           # migrations
│   └── tests/
├── frontend/               # React/Next.js (added Phase 2)
├── pipelines/               # ingestion/transform/quality (added Phase 3+)
├── docker/
├── docker-compose.yml
└── .env.example
```

## Status

- [x] Phase 0 — Repo scaffolding, Docker, FastAPI health check, DB connection
- [ ] Phase 1 — Full initial schema + migrations
- [ ] Phase 2 — Job CRUD API + frontend listing page
- [ ] Phase 3 — Ingestion + cleaning/dedup pipeline
- [ ] Phase 4 — Resume upload + matching engine
- [ ] Phase 5 — Application tracker (Kanban + event timeline)
- [ ] Phase 6 — Analytics
- [ ] Phase 7 — Testing pass + CI
