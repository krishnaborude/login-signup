from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token
)
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import (
    Token,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse
)

router = APIRouter()

@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | 
        (User.username == user.username)
    ).first()
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == login_data.username_or_email) |
        (User.username == login_data.username_or_email)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Create access token with both email and username in the token
    access_token = create_access_token(
        data={"sub": user.email, "username": user.username}
    )
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == request.username_or_email) |
        (User.username == request.username_or_email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this username or email address"
        )
    
    # Generate password reset token using the user's email
    reset_token = create_password_reset_token(user.email)
    
    # Store token and expiry in database
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()
    
    return {
        "message": f"Password reset token has been generated and sent to {user.email}",
        "reset_token": reset_token  # This would be removed in production
    }

@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify token
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user by email and token
    user = db.query(User).filter(
        User.email == email,
        User.reset_token == request.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user.password = get_password_hash(request.new_password)
    # Clear reset token
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    
    return {"message": "Password has been successfully reset"}
