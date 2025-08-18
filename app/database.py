from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

# Get database URL and parse it to get components
DATABASE_URL = os.getenv("DATABASE_URL")
# Extract database name from the URL
db_name = DATABASE_URL.split("/")[-1]
# Create URL without database name for initial connection
db_url_without_name = "/".join(DATABASE_URL.split("/")[:-1])

def create_database():
    try:
        # Connect to PostgreSQL server
        connection = psycopg2.connect(db_url_without_name + "/postgres")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database {db_name} created successfully!")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise e

# Create database if it doesn't exist
create_database()

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
