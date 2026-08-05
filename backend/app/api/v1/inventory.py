from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User
from ...services.store_service import StoreService
from ...api.v1.auth import require_current_user

router = APIRouter()

@router.get('')
def get_inventory(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    service = StoreService(db)
    return service.get_user_inventory(user.id)
