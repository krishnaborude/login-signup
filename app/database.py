from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

load_dotenv()

# Get database URL and parse it to get components
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/login_api_db")
# Extract database name from the URL
db_name = DATABASE_URL.split("/")[-1]
# Create URL without database name for initial connection
db_url_without_name = "/".join(DATABASE_URL.split("/")[:-1])

def create_database():
    retries = 5
    while retries > 0:
        try:
            # Connect to PostgreSQL server
            connection = psycopg2.connect(
                db_url_without_name + "/postgres",
                connect_timeout=3
            )
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
            return True
            
        except Exception as e:
            print(f"Attempt {6-retries}/5: Error connecting to database: {e}")
            retries -= 1
            if retries > 0:
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                raise Exception("Failed to connect to PostgreSQL after 5 attempts") from e

# Create the Base class for declarative models
Base = declarative_base()

def init_db():
    # Create database if it doesn't exist
    create_database()
    
    # Create SQLAlchemy engine with connection pool settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=True  # Set to True to see SQL queries
    )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    return engine, SessionLocal

# Initialize database and get engine and SessionLocal
engine, SessionLocal = init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def recreate_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables recreated successfully!")
