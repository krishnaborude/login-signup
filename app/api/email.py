from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from ..core.email_service import EmailService
from ..core.config import settings
from ..db.session import get_db
from ..models.email import EmailHistory

router = APIRouter()

@router.post("/send", status_code=status.HTTP_200_OK)
async def send_email(
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Send email using Gmail SMTP.
    - **to**: Comma-separated email addresses (e.g., "email1@example.com, email2@example.com")
    - **cc**: Optional comma-separated CC email addresses
    - **bcc**: Optional comma-separated BCC email addresses
    - **subject**: Email subject
    - **body**: Email body
    - **attachment**: Optional file attachment
    """
    # Validate email format
    if not to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recipient email address is required"
        )

    # Initialize email service with credentials from settings
    email_service = EmailService(
        gmail_address=settings.GMAIL_ADDRESS,
        app_password=settings.GMAIL_APP_PASSWORD
    )
    
    # Attempt to send the email
    result = email_service.send_email(
        to=to,
        subject=subject,
        body=body,
        cc=cc,
        bcc=bcc,
        attachment=attachment,
        db=db  # Pass the database session
    )
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to send email")
        )
    
    return {
        "message": "Email sent successfully",
        "recipients": {
            "to": [addr.strip() for addr in to.split(",") if addr.strip()],
            "cc": [addr.strip() for addr in (cc or "").split(",") if addr.strip()],
            "bcc": [addr.strip() for addr in (bcc or "").split(",") if addr.strip()]
        }
    }

@router.get("/history", response_model=List[dict])
async def get_email_history(
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get email sending history
    - **days**: Optional number of days to look back
    """
    query = db.query(EmailHistory)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(EmailHistory.sent_at >= cutoff_date)
    
    emails = query.order_by(EmailHistory.sent_at.desc()).all()
    
    return [
        {
            "id": email.id,
            "sender_email": email.sender_email,
            "to_recipients": email.to_recipients,
            "cc_recipients": email.cc_recipients,
            "bcc_recipients": email.bcc_recipients,
            "subject": email.subject,
            "body": email.body,
            "attachment_name": email.attachment_name,
            "sent_at": email.sent_at
        }
        for email in emails
    ]
