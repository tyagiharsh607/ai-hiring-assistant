import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.config import settings
from app.db import get_session
from app.hunar_client import create_call
from app.models import Candidate, Call

router = APIRouter(prefix="/api/screening", tags=["screening"])


class ScreeningCallRequest(BaseModel):
    candidate_name: str
    phone: str
    job_description: str
    role_title: str | None = None


@router.post("/calls")
async def trigger_screening_call(req: ScreeningCallRequest, session: Session = Depends(get_session)):
    if not settings.hunar_screening_agent_id:
        raise HTTPException(500, "HUNAR_SCREENING_AGENT_ID is not configured")

    candidate = Candidate(name=req.candidate_name, phone=req.phone, title=req.role_title, source="manual")
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    call = Call(candidate_id=candidate.id, flow="screening")
    session.add(call)
    session.commit()
    session.refresh(call)

    request_id = f"screen-{call.id}-{uuid.uuid4().hex[:8]}"
    callback_url = f"{settings.public_base_url}/api/webhooks/hunar"

    hunar_resp = await create_call(
        agent_id=settings.hunar_screening_agent_id,
        callee_name=req.candidate_name,
        mobile_number=req.phone,
        custom_data={"job_description": req.job_description, "role_title": req.role_title or ""},
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
