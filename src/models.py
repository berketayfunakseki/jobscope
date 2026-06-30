from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    canton = Column(String, nullable=True)
    source = Column(String)              # ör. "jobs.ch", "linkedin"
    url = Column(String, unique=True)
    description = Column(String, nullable=True)
    score = Column(Float, nullable=True)  # eşleşme skoru, sonra dolduracağız
    applied = Column(Boolean, default=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())