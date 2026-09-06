import json

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy import and_, or_

from app.db import get_session
from app.hunar_client import get_call
from app.models import Call, Candidate

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "NOT_CONNECTED", "CANCELLED"}


@router.post("/sync")
async def sync_calls(session: Session = Depends(get_session)):
    """Fallback for when the Hunar webhook hasn't (yet) reached us: poll Hunar directly
    for any call that isn't fully resolved yet and update our copy from it.

    Hunar populates `result` asynchronously, a bit *after* status flips to COMPLETED -
    so a call sitting at COMPLETED with no result yet still needs to be re-polled, as
    long as someone was actually engaged (a call that never connected will never get a
    result, so don't poll those forever)."""
    pending = session.exec(
        select(Call).where(
            Call.hunar_call_id.is_not(None),
            or_(
                Call.status.not_in(TERMINAL_STATUSES),
                and_(Call.result_json.is_(None), Call.engagement_status == "ENGAGED"),
            ),
        )
    ).all()

    updated = 0
    for call in pending:
        if not call.hunar_call_id:
            continue
        try:
            data = await get_call(call.hunar_call_id)
        except Exception:
            continue

        call.status = data.get("status", call.status)
        call.engagement_status = data.get("engagement_status") or call.engagement_status
        call.answered_by = data.get("answered_by") or call.answered_by
        call.recording_url = data.get("recording_url") or call.recording_url
        if data.get("result"):
            call.result_json = json.dumps(data["result"])
        session.add(call)
        updated += 1

    session.commit()
    return {"synced": updated}


@router.get("/calls")
def list_calls(session: Session = Depends(get_session)):
    calls = session.exec(select(Call).order_by(Call.created_at.desc())).all()

    out = []
    for call in calls:
        candidate = session.get(Candidate, call.candidate_id) if call.candidate_id else None
        out.append(
            {
                "call_id": call.id,
                "flow": call.flow,
                "status": call.status,
                "engagement_status": call.engagement_status,
                "answered_by": call.answered_by,
                "candidate_name": candidate.name if candidate else None,
                "candidate_phone": candidate.phone if candidate else None,
                "candidate_title": candidate.title if candidate else None,
                "summary": call.summary,
                "transcript": call.transcript,
                "recording_url": call.recording_url,
                "result": json.loads(call.result_json) if call.result_json else None,
                "created_at": call.created_at.isoformat(),
            }
        )
    return out
