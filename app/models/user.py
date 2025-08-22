from sqlalchemy import Column, String, DateTime, Integer
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
