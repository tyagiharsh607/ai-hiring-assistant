import hashlib
import hmac
import base64
from typing import Any

import httpx

from app.config import settings

HEADERS = {
    "X-API-Key": settings.hunar_api_key,
    "Content-Type": "application/json",
}


async def create_call(
    agent_id: str,
    callee_name: str,
    mobile_number: str,
    custom_data: dict[str, Any],
    request_id: str,
    callback_url: str,
) -> dict:
    payload = {
        "agent_id": agent_id,
        "callee_name": callee_name,
        "mobile_number": mobile_number,
        "custom_data": custom_data,
        "request_id": request_id,
    }
    # Hunar requires callback URLs to be https - skip in local dev (http://localhost) and
    # fall back to polling get_call() instead.
    if callback_url.startswith("https://"):
        payload["callback_config"] = {
            "call_status_callback_url": callback_url,
            "call_result_callback_url": callback_url,
            "call_summary_callback_url": callback_url,
        }
    async with httpx.AsyncClient(base_url=settings.hunar_base_url, headers=HEADERS, timeout=30) as client:
        resp = await client.post("/calls/", json=payload)
        resp.raise_for_status()
        return resp.json()


async def get_call(call_id: str) -> dict:
    async with httpx.AsyncClient(base_url=settings.hunar_base_url, headers=HEADERS, timeout=30) as client:
        resp = await client.get(f"/calls/{call_id}/")
        resp.raise_for_status()
        return resp.json()


def verify_webhook_signature(raw_body: bytes, timestamp: str, signature: str) -> bool:
    message = f"{timestamp}.{raw_body.decode()}".encode()
    expected = base64.b64encode(
        hmac.new(settings.hunar_api_key.encode(), message, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)
