import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from ..models.email import EmailHistory

class EmailService:
    def __init__(self, gmail_address: str, app_password: str):
        self.gmail_address = gmail_address
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def _parse_email_addresses(self, email_str: Optional[str]) -> list[str]:
        """Parse comma-separated email addresses and return a list of clean addresses"""
        if not email_str:
            return []
        return [addr.strip() for addr in email_str.split(",") if addr.strip()]

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachment: Optional[UploadFile] = None,
        db: Session = None
    ) -> dict:
        try:
            # Parse email addresses
            to_list = self._parse_email_addresses(to)
            cc_list = self._parse_email_addresses(cc)
            bcc_list = self._parse_email_addresses(bcc)

            if not to_list:
                return {"success": False, "message": "No valid 'To' recipients provided"}

            # Create message container
            message = MIMEMultipart()
            message["From"] = self.gmail_address
            message["To"] = ", ".join(to_list)
            message["Subject"] = subject

            # Add CC recipients if provided
            if cc_list:
                message["Cc"] = ", ".join(cc_list)

            # Add the body to the email
            message.attach(MIMEText(body, "plain"))

            # Add attachment if provided
            if attachment:
                part = MIMEApplication(
                    attachment.file.read(),
                    Name=os.path.basename(attachment.filename)
                )
                part['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
                message.attach(part)

            # Create SMTP session
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.app_password)

                # Combine all recipients
                all_recipients = to_list + cc_list + bcc_list

                # Send email
                server.send_message(message, self.gmail_address, all_recipients)

                # Store email history in database if db session is provided
                if db:
                    email_history = EmailHistory(
                        sender_email=self.gmail_address,
                        to_recipients=", ".join(to_list),
                        cc_recipients=", ".join(cc_list) if cc_list else None,
                        bcc_recipients=", ".join(bcc_list) if bcc_list else None,
                        subject=subject,
                        body=body,
                        attachment_name=attachment.filename if attachment else None
                    )
                    db.add(email_history)
                    db.commit()
                    db.refresh(email_history)

                return {
                    "success": True,
                    "message": "Email sent successfully",
                    "recipients": {
                        "to": to_list,
                        "cc": cc_list,
                        "bcc": bcc_list
                    }
                }

        except Exception as e:
            error_message = str(e)
            
            # Store failed attempt in database if db session is provided
            if db:
                # Do not store failed attempts in history
                db.add(email_history)
                db.commit()
                db.refresh(email_history)
            
            return {
                "success": False,
                "message": f"Failed to send email: {error_message}"
            }
