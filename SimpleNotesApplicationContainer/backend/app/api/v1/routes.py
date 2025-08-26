from fastapi import FastAPI
from fastapi import APIRouter

from app.api.v1 import auth, users, notes, taxonomy

openapi_tags = [
    {"name": "auth", "description": "User authentication and verification routes"},
    {"name": "users", "description": "User profile and privacy settings"},
    {"name": "notes", "description": "Notes CRUD, attachments, search, and bulk"},
    {"name": "taxonomy", "description": "Tags and categories"},
    {"name": "websocket", "description": "WebSocket usage info"},
]

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, tags=["auth"], prefix="/auth")
api_router.include_router(users.router, tags=["users"], prefix="/users")
api_router.include_router(notes.router, tags=["notes"], prefix="/notes")
api_router.include_router(taxonomy.router, tags=["taxonomy"], prefix="/taxonomy")

# PUBLIC_INTERFACE
def register_routes(app: FastAPI) -> None:
    """Attach versioned API routers to the app."""
    app.include_router(api_router)
