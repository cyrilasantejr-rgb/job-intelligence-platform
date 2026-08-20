from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class JobCreate(BaseModel):
    """
    What the client sends to create a job.

    company_name is a plain string rather than a company_id — the service
    layer looks up or creates the Company record, so the caller never needs
    to know our internal IDs.
    """

    company_name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    category: str | None = None
    employment_type: str | None = None  # 'Internship' | 'New Grad'
    location: str | None = None
    work_mode: str | None = None  # 'Remote' | 'Hybrid' | 'On-site'
    salary_min: float | None = None
    salary_max: float | None = None
    description: str | None = None
    application_url: str | None = None
    date_posted: date | None = None
    deadline: date | None = None


class JobRead(BaseModel):
    """What the API returns for a single job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str | None
    employment_type: str | None
    location: str | None
    work_mode: str | None
    salary_min: float | None
    salary_max: float | None
    description: str | None
    application_url: str | None
    date_posted: date | None
    deadline: date | None
    created_at: datetime
    company: CompanyRead


class JobListResponse(BaseModel):
    """Paginated list response for GET /jobs."""

    items: list[JobRead]
    total: int
    page: int
    page_size: int
