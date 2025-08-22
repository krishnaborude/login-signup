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
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import (
    Token,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    PasswordResetSuccessResponse
)

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email is already registered
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        display_name=user.display_name,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add welcome message to response
    setattr(db_user, 'welcome_message', f"Welcome to the platform, {db_user.display_name}!")
    return db_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token with email and display_name
    access_token = create_access_token(
        data={"sub": user.email, "display_name": user.display_name}
    )
    return {
        "message": "Login successful",
        "welcome_message": f"Welcome back, {user.display_name}!",
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email address"
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

@router.post("/reset-password", response_model=PasswordResetSuccessResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
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
        
        # Hash the new password and update user
        user.password = get_password_hash(request.new_password)
        # Clear reset token
        user.reset_token = None
        user.reset_token_expires = None
        
        # Commit changes within try block to ensure rollback on error
        db.commit()
        
        return PasswordResetSuccessResponse(message="Password has been successfully reset")
        
    except Exception as e:
        db.rollback()  # Rollback any changes if error occurs
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting password"
        ) from e
