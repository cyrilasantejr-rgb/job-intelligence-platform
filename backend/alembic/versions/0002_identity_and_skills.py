"""users, resumes, skills, job_skills, user_skills

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-20

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("version_label", sa.String(), nullable=True),
        sa.Column("parsed_text", sa.Text(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
    )

    op.create_table(
        "job_skills",
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), primary_key=True),
        sa.Column("importance", sa.String(), nullable=True),
    )

    op.create_table(
        "user_skills",
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("user_skills")
    op.drop_table("job_skills")
    op.drop_table("skills")
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")
    op.drop_table("users")
