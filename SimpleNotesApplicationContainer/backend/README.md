# SimpleNotes Backend (FastAPI)

FastAPI backend providing authentication, notes CRUD with categories/tags, advanced search, bulk actions, attachments, and privacy settings.

## Run locally

1. Ensure PostgreSQL is available and .env is configured (see `.env.example`)
2. Create venv and install dependencies:
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

3. Run the server:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Open http://localhost:8000/docs for API docs.

## Environment variables

See `.env.example` for all variables.
Note: Do not commit real secrets. Orchestrator will set variables in .env at runtime.

## Database migrations

This scaffold uses SQLAlchemy Core/ORM with auto-create tables on startup (for simplicity in this template).
In production, use Alembic migrations.

## Email / Analytics / Backups

This template includes integration stubs:
- EmailService: for sending verification and password reset emails
- AnalyticsService: for tracking events
- BackupService: for exporting data (stub)

Replace stubs with actual implementations and provider credentials.

## Folder structure

app/
  core/            # Config, security, dependencies, email/analytics stubs
  models/          # SQLAlchemy ORM models
  schemas/         # Pydantic models
  services/        # Business logic services
  api/             # Routers for endpoints
  main.py          # FastAPI app entrypoint

uploads/
  attachments/     # File uploads for notes (local dev only)

## Security notes

- JWT access and refresh tokens via HTTPOnly cookies or Authorization header
- Passwords hashed with bcrypt
- CORS configured for local React dev server
- Rate limiting and CSRF not included in this template (add for production)
