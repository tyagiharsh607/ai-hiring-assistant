import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.config import settings
from app.db import get_session
from app.hunar_client import create_call
from app.models import Candidate, Call, JobDescription
from app.pdl_client import search_people

router = APIRouter(prefix="/api/reachout", tags=["reachout"])


class SearchRequest(BaseModel):
    job_description: str
    role_title: str  # e.g. "software engineer" - used as the PDL job_title_role filter
    location: str | None = None
    limit: int = 10


@router.post("/search")
async def search_candidates(req: SearchRequest, session: Session = Depends(get_session)):
    jd = JobDescription(text=req.job_description, role_title=req.role_title)
    session.add(jd)
    session.commit()
    session.refresh(jd)

    people = await search_people(req.role_title, req.location, req.limit)
    return {"job_description_id": jd.id, "candidates": people}


class ReachoutCallRequest(BaseModel):
    job_description_id: int
    name: str
    phone: str
    email: str | None = None
    title: str | None = None
    company: str | None = None


@router.post("/calls")
async def trigger_reachout_call(req: ReachoutCallRequest, session: Session = Depends(get_session)):
    if not settings.hunar_reachout_agent_id:
        raise HTTPException(500, "HUNAR_REACHOUT_AGENT_ID is not configured")

    jd = session.get(JobDescription, req.job_description_id)
    if not jd:
        raise HTTPException(404, "job description not found")

    candidate = Candidate(
        name=req.name,
        phone=req.phone,
        email=req.email,
        title=req.title,
        company=req.company,
        source="pdl",
        job_description_id=jd.id,
    )
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    call = Call(candidate_id=candidate.id, flow="reachout")
    session.add(call)
    session.commit()
    session.refresh(call)

    request_id = f"reach-{call.id}-{uuid.uuid4().hex[:8]}"
    callback_url = f"{settings.public_base_url}/api/webhooks/hunar"

    hunar_resp = await create_call(
        agent_id=settings.hunar_reachout_agent_id,
        callee_name=req.name,
        mobile_number=req.phone,
        custom_data={"job_description": jd.text, "role_title": jd.role_title or ""},
        request_id=request_id,
        callback_url=callback_url,
    )

    call.hunar_call_id = hunar_resp.get("id") or hunar_resp.get("call_id")
    call.request_id = request_id
    call.status = hunar_resp.get("status", "INITIATED")
    session.add(call)
    session.commit()
    session.refresh(call)

    return {"call_id": call.id, "hunar_call_id": call.hunar_call_id, "status": call.status}
