from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import dashboard, reachout, screening, webhooks

app = FastAPI(title="AI Hiring Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(screening.router)
app.include_router(reachout.router)
app.include_router(webhooks.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"ok": True}
