from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

APPLICATION_STATUSES = [
    "Saved",
    "Applied",
    "Online Assessment",
    "Recruiter Screen",
    "Technical Interview",
    "Final Interview",
    "Offer",
    "Rejected",
    "Withdrawn",
]


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    location: str | None
    company_name: str = Field(validation_alias="company")

    @classmethod
    def from_job(cls, job) -> "JobSummary":
        return cls(id=job.id, title=job.title, location=job.location, company=job.company.name)


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: int | None = None
    notes: str | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    resume_id: int | None
    current_status: str
    date_applied: date | None
    recruiter_contact: str | None
    notes: str | None
    created_at: datetime


class ApplicationDetail(ApplicationRead):
    job: JobSummary


class ApplicationStatusUpdate(BaseModel):
    new_status: str


class EventTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    display_name: str
    maps_to_status: str | None


class ApplicationEventCreate(BaseModel):
    event_type_code: str
    event_date: datetime | None = None
    source: str | None = None
    sender: str | None = None
    subject: str | None = None
    notes: str | None = None
    is_automated: bool | None = None
    requires_response: bool = False
    responded: bool = False
    response_date: datetime | None = None
    next_action: str | None = None
    deadline: datetime | None = None


class ApplicationEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    event_type: EventTypeRead
    event_date: datetime
    recorded_at: datetime
    source: str | None
    sender: str | None
    subject: str | None
    notes: str | None
    is_automated: bool | None
    requires_response: bool
    responded: bool
    response_date: datetime | None
    next_action: str | None
    deadline: datetime | None
    created_by: str
