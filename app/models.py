from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Load database URL from environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create a database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create a base class for models
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Model (Authentication)
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    avatar_url = Column(String, nullable=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)
