from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.db.session import get_session, Base, engine
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserPublic
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.email import EmailService, generate_email_token, verify_email_token
from app.core.config import settings
from app.core.integrations import AnalyticsService

# Create DB tables on startup (for template simplicity)
Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.post("/register", response_model=UserPublic, summary="Register user", description="Create a new user and send verification email.")
def register(payload: UserCreate, db: Session = Depends(get_session)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_verified=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email
    token = generate_email_token(user.id, "verify")
    verification_link = f"{settings.EMAIL_VERIFICATION_REDIRECT_URL}?token={token}"
    EmailService().send_email(
        to_email=user.email,
        subject="Verify your SimpleNotes account",
        body=f"Click to verify: {verification_link}",
    )
    AnalyticsService().track(user.id, "user_registered", {"email": user.email})
    return user

@router.post("/login", response_model=TokenResponse, summary="Login", description="Authenticate user via email and password.")
def login(payload: UserLogin, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    token = create_access_token(str(user.id))
    AnalyticsService().track(user.id, "user_logged_in", None)
    return TokenResponse(access_token=token)

@router.post("/verify", response_model=UserPublic, summary="Verify email", description="Verify a user's email using the token sent via email.")
def verify_email(token: str = Form(...), db: Session = Depends(get_session)):
    data = verify_email_token(token)
    if not data or data.get("purpose") != "verify":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, int(data["uid"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/request-password-reset", summary="Request password reset", description="Generate a password reset token and send it via email.")
def request_password_reset(email: EmailStr = Form(...), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't leak user existence
        return {"message": "If the email exists, a reset link has been sent."}
    token = generate_email_token(user.id, "reset")
    reset_link = f"{settings.PASSWORD_RESET_REDIRECT_URL}?token={token}"
    EmailService().send_email(
        to_email=user.email,
        subject="Reset your SimpleNotes password",
        body=f"Reset link: {reset_link}",
    )
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password", summary="Reset password", description="Use the token to set a new password.")
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_session)):
    data = verify_email_token(token)
    if not data or data.get("purpose") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, int(data["uid"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    return {"message": "Password updated successfully"}
