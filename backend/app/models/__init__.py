"""
Import every ORM model here so that:
  1. Alembic's env.py can do `from app.models import *` and see the full
     metadata for autogenerate.
  2. Relationship string references (e.g. "Company") resolve correctly
     regardless of which module triggers the import first.

Add new models to this list as they're created in later phases.
"""

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.company import Company
from app.models.event_type import EventType
from app.models.ingestion_run import IngestionRun
from app.models.interview import Interview
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.job_skill import JobSkill, UserSkill
from app.models.job_source import JobSource
from app.models.raw_posting import RawPosting
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.user import User

__all__ = [
    "Application",
    "ApplicationEvent",
    "Company",
    "EventType",
    "IngestionRun",
    "Interview",
    "Job",
    "JobMatch",
    "JobSkill",
    "JobSource",
    "RawPosting",
    "Resume",
    "Skill",
    "User",
    "UserSkill",
]
