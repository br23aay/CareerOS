"""
core/database.py — SQLite persistence via SQLAlchemy, one schema for the
whole OS. Swap the URL for Postgres later without touching department code.
"""

from datetime import datetime, timezone
import sys
from pathlib import Path

from sqlalchemy import (Column, Integer, String, Float, Text, Boolean,
                        DateTime, ForeignKey, create_engine, UniqueConstraint)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core import config  # noqa: E402

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    source = Column(String(40)); source_id = Column(String(120))
    title = Column(String(300)); company = Column(String(200))
    location = Column(String(200)); description = Column(Text)
    salary_min = Column(Integer); salary_max = Column(Integer)
    url = Column(String(600)); posted = Column(String(60))
    category = Column(String(60))
    # matcher
    score = Column(Float, default=0.0); verdict = Column(String(20))
    reasons = Column(Text); matched_skills = Column(Text)
    recommended_cv = Column(String(60))
    # verification
    ghost_score = Column(Float)          # 0-100, higher = more suspicious
    company_verified = Column(Boolean, default=False)
    fetched_at = Column(DateTime, default=_now)
    __table_args__ = (UniqueConstraint("source", "source_id",
                                       name="uq_src_srcid"),)
    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    # found->matched->applied->contacted->interview->rejected->offer->accepted
    status = Column(String(30), default="found")
    cv_used = Column(String(60)); cover_letter_path = Column(String(600))
    notes = Column(Text); updated_at = Column(DateTime, default=_now,
                                              onupdate=_now)
    job = relationship("Job", back_populates="applications")


class Contact(Base):                      # Outreach / CRM
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(160)); role = Column(String(120))
    company = Column(String(200)); linkedin = Column(String(300))
    email = Column(String(200)); trust_score = Column(Float)
    history = Column(Text); created_at = Column(DateTime, default=_now)


class InterviewPrep(Base):                # Interview department
    __tablename__ = "interview_preps"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    company_report = Column(String(600)); guide_path = Column(String(600))
    created_at = Column(DateTime, default=_now)


class Outcome(Base):                      # Learning / Analytics
    __tablename__ = "outcomes"
    id = Column(Integer, primary_key=True)
    cv_version = Column(String(60)); job_source = Column(String(60))
    applied = Column(Boolean, default=False)
    replied = Column(Boolean, default=False)
    interviewed = Column(Boolean, default=False)
    offered = Column(Boolean, default=False)
    recorded_at = Column(DateTime, default=_now)


_engine = create_engine(config.DB_URL, future=True)
SessionLocal = sessionmaker(bind=_engine, future=True)


def init_db():
    Base.metadata.create_all(_engine)


def get_session():
    return SessionLocal()
