from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...db.session import get_db
from ...models.user import User
from ...services.admin_service import AdminService
from ...api.v1.auth import require_current_user

router = APIRouter()

class GrantCoinsRequest(BaseModel):
    amount: int

class UnlockLevelRequest(BaseModel):
    level_num: int

def require_admin_user(user: User = Depends(require_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return user

@router.get('/users')
def list_users(user: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    return service.list_all_users()

@router.post('/users/{target_user_id}/grant-coins')
def grant_coins(target_user_id: int, req: GrantCoinsRequest, user: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    new_bal = service.grant_user_coins(target_user_id, req.amount)
    return {"success": True, "target_user_id": target_user_id, "new_balance": new_bal}

@router.post('/users/{target_user_id}/unlock-levels')
def unlock_levels(target_user_id: int, req: UnlockLevelRequest, user: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    highest = service.unlock_user_levels(target_user_id, req.level_num)
    return {"success": True, "target_user_id": target_user_id, "highest_unlocked_level": highest}

@router.post('/users/{target_user_id}/reset')
def reset_progress(target_user_id: int, user: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    service.reset_user_progress(target_user_id)
    return {"success": True, "target_user_id": target_user_id, "message": "User progress reset to level 1."}
