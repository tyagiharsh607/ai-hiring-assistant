# AI Hiring Assistant

Voice-AI powered candidate screening + people search & reachout, built on [Hunar.ai](https://hunar.ai) voice agents and [People Data Labs](https://peopledatalabs.com) for sourcing.

**Deployed app:** https://ai-hiring-assistant-drab.vercel.app
**Backend API:** https://ai-hiring-assistant-4csg.onrender.com

## What's in here

Two flows share one backend pipeline (create a Hunar voice agent call, Hunar calls the person, webhook/poll stores the transcript + structured result, dashboard shows it):

1. **Screening Call** (`/screening`): enter a candidate + phone + JD, a Hunar voice agent calls them directly and screens them against the JD.
2. **People Search & Reachout** (`/reachout`): paste a JD + role title, People Data Labs finds matching people, you confirm a phone number per candidate and trigger a reachout call.
3. **Dashboard** (`/dashboard`): every call placed, its live status, and the structured answers Hunar's agent extracted from the conversation (plus the recording).

## Architecture

```
Next.js (TS, shadcn/ui)  ──HTTP──▶  FastAPI backend  ──HTTPS──▶  Hunar Voice API (agents/calls)
     screening/reachout/                │   ▲                         │
     dashboard pages                    │   │  webhook (call_result_done,       │
                                        │   └─ call_status_updated, ...) ◀───────┘
                                   SQLite (Candidate / JobDescription / Call)
                                        │
                                        └──HTTPS──▶ People Data Labs (person search)
```

- **Backend** (`backend/`, FastAPI + SQLModel + SQLite): `app/hunar_client.py` wraps the Hunar Voice API (create call, poll call, verify webhook HMAC signature); `app/pdl_client.py` wraps PDL person search; routers under `app/routers/` expose `/api/screening`, `/api/reachout`, `/api/webhooks/hunar`, `/api/dashboard`.
- **Frontend** (`frontend/`, Next.js App Router + TypeScript + shadcn/ui): three pages hitting the backend via `src/lib/api.ts`.
- Hunar's structured extraction (`result_schema` on the agent) is what turns a phone conversation into the JSON shown on the dashboard, no manual transcript parsing.

## Setup

### Backend
```bash
cd backend
python3.13 -m venv .venv && source .venv/bin/activate   # python 3.14 currently breaks sqlmodel/pydantic, use 3.13
pip install -r requirements.txt
cp .env.example .env   # fill in HUNAR_API_KEY, PDL_API_KEY, agent IDs (see below)
python scripts/setup_agents.py   # one-off: creates the two Hunar agents, prints their IDs to paste into .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```

## Environment variables

Backend (`backend/.env`, never committed):
| Var | Notes |
|---|---|
| `HUNAR_API_KEY` | from Hunar; org-scoped, all requests use header `X-API-Key` |
| `HUNAR_SCREENING_AGENT_ID` / `HUNAR_REACHOUT_AGENT_ID` | printed by `scripts/setup_agents.py` |
| `PDL_API_KEY` | People Data Labs API key |
| `PUBLIC_BASE_URL` | must be a public **https** URL in production (Render URL). Hunar rejects non-https webhook URLs, so locally the app falls back to polling (see Known limitations) |

Frontend (`frontend/.env.local`):
| Var | Notes |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | the backend's base URL |

## Deployment

- **Backend → Render**: new Web Service from this repo, root dir `backend`, uses `backend/render.yaml`. Set the secret env vars in the Render dashboard (they're marked `sync: false` in render.yaml so they're never committed). After the first deploy, set `PUBLIC_BASE_URL` to the Render service's own URL and redeploy so outbound webhook URLs point at it.
- **Frontend → Vercel**: import this repo, root dir `frontend`, set `NEXT_PUBLIC_API_BASE_URL` to the Render backend URL.

## Known limitations (by design, given the 3-day API key window)

- **PDL free/trial tier redacts contact info.** Phone/email fields come back as a placeholder rather than the real value unless the plan has PII access, confirmed directly against the live API. So the reachout flow uses PDL for **matching/discovery** (name, title, company, LinkedIn) and has the recruiter confirm/enter the real phone number per candidate before calling, which is realistic behavior anyway.
- **SQLite on Render's free tier is ephemeral**, fine for a graded demo, but data won't survive a redeploy. A real deployment would point `DATABASE_URL` at a managed Postgres instance; no other code changes needed since SQLModel/SQLAlchemy already abstract that.
- **Hunar's calling guardrails** (08:00-21:00 org-local time by default) mean a call placed outside that window sits at `SCHEDULED` until the window reopens. This is Hunar enforcing sane calling hours, not a bug.
- Local dev can't receive Hunar's webhook (`http://localhost` isn't a valid callback URL), so the dashboard also calls a `/api/dashboard/sync` fallback that polls Hunar directly for any call still in a non-terminal state. In production the webhook does the real-time job; sync is just a safety net.

---

## Question 3: attendance tracking without smartphones, with LLMs

**Premise:** no smartphones or apps, but landlines/feature phones, computers, kiosks, and LLMs all exist. Tracking 1000 people across 100 locations, daily.

**Approach: a toll-free IVR line staffed by a voice AI agent, not an app.**

Every location gets its own extension (or a spoken location code) off one central toll-free number. Each employee calls in at arrival and departure from whatever phone is at hand: a landline at the site, a shared feature phone, a payphone if it comes to that, and talks to a voice AI agent, the same mechanism this assignment already builds. There's no app to install, no onboarding, no device dependency: a phone call is the lowest common denominator of "everything else exists."

Identity is confirmed with an employee ID + PIN spoken to the agent (optionally reinforced with simple voiceprint matching over repeated calls to catch buddy-punching), and the agent logs employee, location, and timestamp straight into a central system, the same pipeline as the reachout/screening flow here: call, structured extraction, dashboard.

This is where the LLM does more than transcription:
- **Natural conversation, zero training.** Employees just talk; the agent handles "I'm running 10 minutes late, traffic" as naturally as a plain check-in, and captures the reason as structured data instead of discarding it.
- **Exception handling without a human in the loop.** Missed check-outs, mismatched location codes, or a suspicious pattern (same PIN checking in from two locations minutes apart) get flagged and the agent can immediately call back to clarify, rather than waiting for HR to notice days later.
- **A daily digest for HR**, generated by the LLM from the day's raw records, across all 100 locations: who's absent, who's late and why, which locations are trending late this week, instead of HR paging through 1000 raw log lines by hand.
- **Dispute resolution.** An employee disputing a marked absence can call the same line and have the agent pull their record and reason about it conversationally, rather than filing a ticket.

For the rare site with genuinely no working phone, the fallback is a physical device (card-swipe or keypad box, since "everything else" includes hardware) wired into the same backend. The LLM stays purely on the back office side there (reporting, anomaly detection), never on the front end.

Why this beats trying to reinvent an app with hardware tricks: it needs zero new hardware at 99% of sites, has no learning curve, degrades gracefully, and turns HR's job from "chase 1000 rows of raw data across 100 locations" into "read one daily summary and follow up on what's flagged."
