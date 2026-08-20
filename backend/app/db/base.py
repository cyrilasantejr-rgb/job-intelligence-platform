"""
Shared SQLAlchemy declarative base.

Every ORM model in app/models/ should inherit from this `Base`. Alembic's
env.py imports this (plus all models) so autogenerate can detect the full
schema.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
