from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import assistant, dashboard, emails, settings, sync, tickets
from app.services.email_sync import sync_emails
from app.services.vector_store import init_vector_store

settings_cfg = get_settings()
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_vector_store()

    if not settings_cfg.dev_mode:
        scheduler.add_job(
            sync_emails,
            "interval",
            minutes=settings_cfg.sync_interval_minutes,
            id="email_sync",
        )
        scheduler.start()

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="IT Support Manager",
    description="IT Support Manager pro Marbes – správa ticketů a emailů",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router, prefix="/api", tags=["tickets"])
app.include_router(emails.router, prefix="/api", tags=["emails"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(sync.router, prefix="/api", tags=["sync"])
app.include_router(assistant.router, prefix="/api", tags=["assistant"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
