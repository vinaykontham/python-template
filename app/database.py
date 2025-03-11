from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Create a database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base() 
# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
DATABASE_URL = "sqlite:///./test.db"  # Change to PostgreSQL URL if needed
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    avatar_url = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)