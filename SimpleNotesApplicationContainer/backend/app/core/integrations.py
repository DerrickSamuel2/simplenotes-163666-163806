from app.core.config import settings

class AnalyticsService:
    def __init__(self) -> None:
        self.enabled = settings.ANALYTICS_ENABLE
        self.write_key = settings.ANALYTICS_WRITE_KEY

    # PUBLIC_INTERFACE
    def track(self, user_id: int | None, event: str, properties: dict | None = None) -> None:
        """Track analytics events (stub)."""
        if not self.enabled:
            return
        print(f"[Analytics] user={user_id} event={event} props={properties or {}}")

class BackupService:
    def __init__(self) -> None:
        self.enabled = settings.BACKUP_ENABLE
        self.bucket = settings.BACKUP_BUCKET
        self.provider = settings.BACKUP_PROVIDER

    # PUBLIC_INTERFACE
    def export_user_data(self, user_id: int) -> str:
        """Export and store user data to backup provider (stub)."""
        if not self.enabled:
            return "Backups disabled"
        # TODO: implement provider-specific upload
        return f"backup://{self.provider}/{self.bucket}/user-{user_id}.json"
