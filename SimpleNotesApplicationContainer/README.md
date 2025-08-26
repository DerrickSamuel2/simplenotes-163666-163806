# SimpleNotes Monolithic Application

This container hosts a monolithic app with:
- React frontend (in this folder)
- FastAPI backend (in backend/)
- PostgreSQL database (configured via environment variables)
- Auth (register, verify email, login), notes CRUD with attachments, categories/tags, search, bulk ops
- Privacy settings, integration stubs for email, analytics, backups

## Quick start (two terminals)

Terminal 1 (backend):
  cd SimpleNotesApplicationContainer/backend
  cp .env.example .env  # Set values as needed
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Terminal 2 (frontend):
  cd SimpleNotesApplicationContainer
  npm install
  # Configure API base if different:
  # export REACT_APP_API_BASE=http://localhost:8000/api/v1
  npm start

Open http://localhost:3000

API docs: http://localhost:8000/docs

## Environment variables

- Frontend:
  - REACT_APP_API_BASE: Base URL for backend API (default http://localhost:8000/api/v1)

- Backend: see backend/.env.example for full list
  - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  - SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, etc.
  - CORS_ORIGINS should include http://localhost:3000 for local dev
  - EMAIL_* flags for email verification/reset (stubs)

## Notes

- Attachments are stored locally in backend/uploads/attachments and served at /uploads/*
- Replace integration stubs with your provider credentials for production
- For production, add HTTPS, proper cookie security, rate limiting, CSRF, and real migrations
