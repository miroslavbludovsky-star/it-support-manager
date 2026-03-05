from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.email_sync import sync_emails

router = APIRouter()

_last_sync: dict = {"status": "idle", "last_run": None, "error": None}


@router.post("/sync/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    """Manually trigger email sync."""
    _last_sync["status"] = "running"
    try:
        count = await sync_emails(db=db)
        _last_sync["status"] = "completed"
        _last_sync["last_run"] = datetime.utcnow().isoformat()
        _last_sync["error"] = None
        return {"status": "ok", "emails_synced": count}
    except Exception as e:
        _last_sync["status"] = "error"
        _last_sync["error"] = str(e)
        return {"status": "error", "detail": str(e)}


@router.get("/sync/status")
async def sync_status():
    return _last_sync
