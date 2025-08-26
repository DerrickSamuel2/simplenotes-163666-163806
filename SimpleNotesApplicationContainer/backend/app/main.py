from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.routes import register_routes, openapi_tags

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application with routes, CORS, and static mounts."""
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Backend API for SimpleNotes with auth, notes, categories/tags, search, and integrations.",
        version="1.0.0",
        openapi_tags=openapi_tags,
        contact={"name": "SimpleNotes", "url": "https://example.com"},
    )

    # CORS setup
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static serving for local attachments
    app.mount(
        "/uploads",
        StaticFiles(directory=str(settings.UPLOADS_DIR)),
        name="uploads",
    )

    # Register API routes
    register_routes(app)

    @app.get("/ws-info", tags=["websocket"], summary="WebSocket usage", description="No real-time endpoints in this template. Reserved for future use.")
    def ws_info():
        return {
            "message": "No WebSocket endpoints in this template. This endpoint documents future real-time usage."
        }

    return app


app = create_app()
