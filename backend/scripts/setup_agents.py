"""One-off script: creates the two Hunar voice agents this project needs
(screening + reachout) and prints the agent_ids to paste into .env.

Run once from backend/: python scripts/setup_agents.py
"""

import asyncio

import httpx

from app.config import settings

HEADERS = {"X-API-Key": settings.hunar_api_key, "Content-Type": "application/json"}

SCREENING_AGENT = {
    "name": "Candidate Screening Agent",
    "language": "ENGLISH",
    "voice_persona": "NEHA",
    "persona_name": "Seema",
    "agent_prompt": (
        "You are {persona_name}, a recruiter calling {callee_name} to screen them for a role. "
        "Job description: {job_description}. Role: {role_title}. "
        "Ask about relevant experience, current CTC, expected CTC, notice period, and key skills "
        "matching the job description. Be warm, concise, and professional. Keep the call short."
    ),
    "objective": "Screen the candidate against the job description and collect structured hiring signals.",
    "introduction": "Hi {callee_name}, this is {persona_name} calling about the {role_title} role. Do you have a couple of minutes?",
    "result_prompt": "Extract the candidate's screening answers as structured fields from this conversation.",
    "result_schema": {
        "years_experience": "",
        "current_ctc": "",
        "expected_ctc": "",
        "notice_period": "",
        "key_skills": "",
        "interested": "",
        "fit_summary": "",
    },
}

REACHOUT_AGENT = {
    "name": "Sourcing Reachout Agent",
    "language": "ENGLISH",
    "voice_persona": "ROY",
    "persona_name": "Arjun",
    "agent_prompt": (
        "You are {persona_name}, a recruiter cold-calling {callee_name} about a job opportunity. "
        "Job description: {job_description}. Role: {role_title}. "
        "Introduce the opportunity briefly, check if they're open to hearing more, gauge interest, "
        "current role/notice period, and expected CTC if they're interested. Be brief and respectful "
        "of their time; if not interested, thank them and end the call politely."
    ),
    "objective": "Gauge interest in the role and collect structured reachout signals.",
    "introduction": "Hi {callee_name}, this is {persona_name}, a recruiter. I came across your profile for a {role_title} role - do you have a quick minute?",
    "result_prompt": "Extract the candidate's interest and reachout answers as structured fields from this conversation.",
    "result_schema": {
        "interested": "",
        "current_role": "",
        "notice_period": "",
        "expected_ctc": "",
        "best_time_to_call_back": "",
    },
}


async def create_agent(payload: dict) -> str:
    async with httpx.AsyncClient(
        base_url=settings.hunar_base_url, headers=HEADERS, timeout=30
    ) as client:
        resp = await client.post("/agents/", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("id") or data.get("agent_id")


async def main():
    screening_id = await create_agent(SCREENING_AGENT)
    print(f"HUNAR_SCREENING_AGENT_ID={screening_id}")
    reachout_id = await create_agent(REACHOUT_AGENT)
    print(f"HUNAR_REACHOUT_AGENT_ID={reachout_id}")


if __name__ == "__main__":
    asyncio.run(main())
