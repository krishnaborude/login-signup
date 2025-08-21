from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta

from app import models, schemas, auth
from app.database import engine, get_db, create_tables_if_not_exist

# Initialize database tables without dropping existing data
create_tables_if_not_exist()

app = FastAPI(
    title="Authentication API",
    description="API for user signup and login",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Authentication API",
    }

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | 
        (models.User.username == user.username)
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
    
    # The password validation is automatically done by Pydantic
    # Create new user with hashed password
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post(
    "/login",
    response_model=schemas.Token,
    summary="Login with username/email and password",
    description="Authenticate using either your username or email along with your password",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username_or_email": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["username_or_email", "password"],
                        "example": {
                            "username_or_email": "your_username_or_email",
                            "password": "your_password"
                        }
                    }
                }
            }
        }
    }
)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Find user by email or username
    user = db.query(models.User).filter(
        (models.User.email == login_data.username_or_email) |
        (models.User.username == login_data.username_or_email)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Verify password
    if not auth.verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Create access token with both email and username in the token
    access_token = auth.create_access_token(
        data={"sub": user.email, "username": user.username}
    )
    return {
        "message": "Login successful",
        "access_token": access_token
    }

@app.post("/forgot-password", response_model=schemas.PasswordResetResponse)
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Find user by email or username
    user = db.query(models.User).filter(
        (models.User.email == request.username_or_email) |
        (models.User.username == request.username_or_email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this username or email address"
        )
    
    # Generate password reset token using the user's email
    reset_token = auth.create_password_reset_token(user.email)
    
    # Store token and expiry in database
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()
    
    return {
        "message": f"Password reset token has been generated and sent to {user.email}",
        "reset_token": reset_token  # This would be removed in production
    }

@app.post("/reset-password", response_model=schemas.PasswordResetResponse)
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify token
    email = auth.verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user by email and token
    user = db.query(models.User).filter(
        models.User.email == email,
        models.User.reset_token == request.token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user.password = auth.get_password_hash(request.new_password)
    # Clear reset token
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    
    return {"message": "Password has been successfully reset"}
