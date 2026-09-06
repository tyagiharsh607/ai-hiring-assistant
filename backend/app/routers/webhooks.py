import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session, select

from app.db import get_session
from app.hunar_client import verify_webhook_signature
from app.models import Call

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/hunar")
async def hunar_webhook(
    request: Request,
    session: Session = Depends(get_session),
    x_hunar_signature: str | None = Header(default=None),
    x_hunar_timestamp: str | None = Header(default=None),
):
    raw_body = await request.body()

    if x_hunar_signature and x_hunar_timestamp:
        if not verify_webhook_signature(raw_body, x_hunar_timestamp, x_hunar_signature):
            raise HTTPException(401, "invalid webhook signature")

    payload = json.loads(raw_body or b"{}")
    call_data = payload.get("call", payload)

    hunar_call_id = call_data.get("id") or call_data.get("call_id")
    request_id = call_data.get("request_id")

    call = None
    if hunar_call_id:
        call = session.exec(select(Call).where(Call.hunar_call_id == hunar_call_id)).first()
    if call is None and request_id:
        call = session.exec(select(Call).where(Call.request_id == request_id)).first()

    if call is None:
        # Nothing to attach this event to yet (e.g. event arrived before we stored the call id).
        return {"ok": True, "matched": False}

    if "status" in call_data:
        call.status = call_data["status"]
    if "engagement_status" in call_data:
        call.engagement_status = call_data["engagement_status"]
    if "answered_by" in call_data:
        call.answered_by = call_data["answered_by"]
    if "transcript" in call_data:
        call.transcript = call_data["transcript"]
    if "summary" in call_data:
        call.summary = call_data["summary"]
    if "result" in call_data:
        call.result_json = json.dumps(call_data["result"])

    session.add(call)
    session.commit()

    return {"ok": True, "matched": True}
