# Import all the models, so that Base has them before being imported by Alembic
from app.db.base_class import Base
from app.models.email import EmailHistory
from app.models.user import User  # This is important for Alembic to detect the User model
