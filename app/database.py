from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# Create a database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base() 
# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
