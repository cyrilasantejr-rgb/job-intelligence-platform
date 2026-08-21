from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_label: str | None
    uploaded_at: datetime


class ResumeUploadResponse(BaseModel):
    resume: ResumeRead
    extracted_skills: list[str]
