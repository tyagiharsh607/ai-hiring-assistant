from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class JobDescription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    role_title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    source: str = "manual"  # manual | pdl
    job_description_id: Optional[int] = Field(default=None, foreign_key="jobdescription.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Call(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: Optional[int] = Field(default=None, foreign_key="candidate.id")
    flow: str  # screening | reachout
    hunar_call_id: Optional[str] = None
    request_id: Optional[str] = None
    status: str = "NOT_STARTED"
    engagement_status: Optional[str] = None
    answered_by: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    result_json: Optional[str] = None  # structured result_schema output, stored as JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
