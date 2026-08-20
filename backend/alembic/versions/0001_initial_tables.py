"""initial tables: companies, job_sources, jobs

Revision ID: 0001
Revises:
Create Date: 2026-08-20

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("normalized_name", sa.String(), nullable=False, unique=True),
        sa.Column("website", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "job_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=True),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id"),
            nullable=False,
        ),
        sa.Column(
            "source_id",
            sa.Integer(),
            sa.ForeignKey("job_sources.id"),
            nullable=True,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("employment_type", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("work_mode", sa.String(), nullable=True),
        sa.Column("salary_min", sa.Numeric(), nullable=True),
        sa.Column("salary_max", sa.Numeric(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("application_url", sa.String(), nullable=True),
        sa.Column("date_posted", sa.Date(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("dedup_hash", sa.String(), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_category", "jobs", ["category"])


def downgrade() -> None:
    op.drop_index("ix_jobs_category", table_name="jobs")
    op.drop_index("ix_jobs_company_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("job_sources")
    op.drop_table("companies")
