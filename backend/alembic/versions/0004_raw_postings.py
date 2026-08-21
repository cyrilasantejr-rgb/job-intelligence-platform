"""raw_postings staging table + jobs.raw_posting_id

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-20

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "raw_postings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("job_sources.id"), nullable=True),
        sa.Column("raw_payload", JSONB(), nullable=False),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_raw_postings_processed", "raw_postings", ["processed"])

    op.add_column(
        "jobs",
        sa.Column(
            "raw_posting_id", sa.Integer(), sa.ForeignKey("raw_postings.id"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("jobs", "raw_posting_id")
    op.drop_index("ix_raw_postings_processed", table_name="raw_postings")
    op.drop_table("raw_postings")
