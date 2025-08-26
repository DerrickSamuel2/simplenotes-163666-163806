from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# PUBLIC_INTERFACE
def generate_email_token(user_id: int, purpose: str) -> str:
    """Generate a signed token for email verification or password reset."""
    return serializer.dumps({"uid": user_id, "purpose": purpose})

# PUBLIC_INTERFACE
def verify_email_token(token: str, max_age: int = 3600 * 24) -> dict | None:
    """Verify a signed token."""
    try:
        return serializer.loads(token, max_age=max_age)
    except Exception:
        return None

class EmailService:
    """Simple email service stub that logs emails to console."""
    def __init__(self, enabled: bool = settings.EMAIL_ENABLE) -> None:
        self.enabled = enabled

    def send_email(self, to_email: str, subject: str, body: str) -> None:
        if not self.enabled:
            print(f"[EmailStub Disabled] To: {to_email} | Subject: {subject}\n{body}")
            return
        # TODO: implement real SMTP provider integration using settings
        print(f"[EmailStub Enabled] Pretending to send email to {to_email}: {subject}")
