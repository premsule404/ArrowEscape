from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User
from ...schemas.progress import CloudSyncRequest, CloudSyncResponse
from ...services.sync_service import SyncService
from ...api.v1.auth import require_current_user

router = APIRouter()

@router.post('/sync', response_model=CloudSyncResponse)
def cloud_sync(sync_req: CloudSyncRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    service = SyncService(db)
    return service.sync_user_progress(user.id, sync_req)
