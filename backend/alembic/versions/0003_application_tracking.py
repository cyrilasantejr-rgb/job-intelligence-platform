"""applications, event tracking, interviews, job_matches, ingestion_runs

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-20

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


# Seed data for event_types — matches the event list from the application
# communication/timeline design. `maps_to_status` is intentionally sparse:
# most events enrich the timeline without moving the Kanban column.
EVENT_TYPES = [
    ("application_submitted", "Application Submitted", "Applied"),
    ("auto_confirmation", "Automated Confirmation Received", None),
    ("recruiter_response", "Recruiter Response Received", None),
    ("user_reply_sent", "My Response Sent", None),
    ("oa_received", "Online Assessment Received", "Online Assessment"),
    ("oa_deadline", "OA Deadline", None),
    ("oa_completed", "OA Completed", None),
    ("recruiter_screen_scheduled", "Recruiter Screen Scheduled", "Recruiter Screen"),
    ("recruiter_screen_completed", "Recruiter Screen Completed", None),
    ("technical_interview_scheduled", "Technical Interview Scheduled", "Technical Interview"),
    ("technical_interview_completed", "Technical Interview Completed", None),
    ("final_interview_scheduled", "Final Interview Scheduled", "Final Interview"),
    ("final_interview_completed", "Final Interview Completed", None),
    ("followup_sent", "Follow-up Email Sent", None),
    ("rejection_received", "Rejection Received", "Rejected"),
    ("offer_received", "Offer Received", "Offer"),
    ("ghosted", "No Response / Ghosted", None),
    ("withdrawn", "Application Withdrawn", "Withdrawn"),
]


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), nullable=True),
        sa.Column("current_status", sa.String(), nullable=False, server_default="saved"),
        sa.Column("date_applied", sa.Date(), nullable=True),
        sa.Column("recruiter_contact", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])
    op.create_index("ix_applications_status", "applications", ["current_status"])

    op.create_table(
        "event_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("maps_to_status", sa.String(), nullable=True),
    )

    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False
        ),
        sa.Column(
            "event_type_id", sa.Integer(), sa.ForeignKey("event_types.id"), nullable=False
        ),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_automated", sa.Boolean(), nullable=True),
        sa.Column("requires_response", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("responded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("response_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_message_id", sa.String(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False, server_default="user"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_application_events_app_date", "application_events", ["application_id", "event_date"]
    )

    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "application_id", sa.Integer(), sa.ForeignKey("applications.id"), nullable=False
        ),
        sa.Column("interview_type", sa.String(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_interviews_application_id", "interviews", ["application_id"])

    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), nullable=False),
        sa.Column("skill_score", sa.Numeric(), nullable=True),
        sa.Column("experience_score", sa.Numeric(), nullable=True),
        sa.Column("semantic_score", sa.Numeric(), nullable=True),
        sa.Column("education_score", sa.Numeric(), nullable=True),
        sa.Column("overall_score", sa.Numeric(), nullable=True),
        sa.Column("matched_skills", JSONB(), nullable=True),
        sa.Column("missing_skills", JSONB(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_job_matches_job_id", "job_matches", ["job_id"])
    op.create_index("ix_job_matches_resume_id", "job_matches", ["resume_id"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("job_sources.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_fetched", sa.Integer(), nullable=True),
        sa.Column("records_new", sa.Integer(), nullable=True),
        sa.Column("records_duplicate", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    # Seed event_types
    event_types_table = sa.table(
        "event_types",
        sa.column("code", sa.String),
        sa.column("display_name", sa.String),
        sa.column("maps_to_status", sa.String),
    )
    op.bulk_insert(
        event_types_table,
        [
            {"code": code, "display_name": display_name, "maps_to_status": maps_to_status}
            for code, display_name, maps_to_status in EVENT_TYPES
        ],
    )


def downgrade() -> None:
    op.drop_table("ingestion_runs")
    op.drop_index("ix_job_matches_resume_id", table_name="job_matches")
    op.drop_index("ix_job_matches_job_id", table_name="job_matches")
    op.drop_table("job_matches")
    op.drop_index("ix_interviews_application_id", table_name="interviews")
    op.drop_table("interviews")
    op.drop_index("ix_application_events_app_date", table_name="application_events")
    op.drop_table("application_events")
    op.drop_table("event_types")
    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_applications_job_id", table_name="applications")
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_table("applications")
