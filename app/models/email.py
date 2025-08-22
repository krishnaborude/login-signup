from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from ..db.base_class import Base

class EmailHistory(Base):
    __tablename__ = "email_history"

    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String, nullable=False)
    to_recipients = Column(String, nullable=False)  # Comma-separated emails
    cc_recipients = Column(String)  # Comma-separated emails
    bcc_recipients = Column(String)  # Comma-separated emails
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    attachment_name = Column(String)  # Store the name of the attachment if any
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
