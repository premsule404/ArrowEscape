from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User
from ...models.sync import CloudSyncQueue
from ...api.v1.auth import require_current_user

router = APIRouter()

@router.get('/status')
def get_sync_status(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    pending = db.query(CloudSyncQueue).filter(CloudSyncQueue.user_id == user.id, CloudSyncQueue.status == 'pending').count()
    synced = db.query(CloudSyncQueue).filter(CloudSyncQueue.user_id == user.id, CloudSyncQueue.status == 'synced').count()
    return {
        "user_id": user.id,
        "pending_syncs": pending,
        "completed_syncs": synced,
        "sync_status": "UP_TO_DATE" if pending == 0 else "SYNCING"
    }
