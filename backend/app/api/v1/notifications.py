from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...db.session import get_db
from ...models.user import User
from ...models.notifications import Notification
from ...api.v1.auth import require_current_user

router = APIRouter()

class CreateNotificationPayload(BaseModel):
    type: str # 'achievement', 'daily', 'friend', 'shop', 'level', 'cloud', 'error', 'system'
    title: str
    content: str
    icon: Optional[str] = "🔔"

@router.get('', response_model=Dict[str, Any])
def get_notifications(unread_only: bool = False, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.read == False)

    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = db.query(Notification).filter(Notification.user_id == user.id, Notification.read == False).count()

    results = []
    for n in notifications:
        results.append({
            "id": n.id,
            "type": n.type,
            "title": n.title or n.type.capitalize(),
            "content": n.content,
            "icon": n.icon or "🔔",
            "read": n.read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else ""
        })

    return {
        "unread_count": unread_count,
        "notifications": results
    }

@router.post('/create')
def create_notification(payload: CreateNotificationPayload, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    notif = Notification(
        user_id=user.id,
        type=payload.type,
        title=payload.title,
        content=payload.content,
        icon=payload.icon or "🔔",
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return {"success": True, "id": notif.id}

@router.put('/read/{notification_id}')
def mark_read(notification_id: int, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notif.read = True
    db.commit()

    return {"success": True}

@router.put('/read-all')
def mark_all_read(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.read == False).update({"read": True})
    db.commit()

    return {"success": True}

@router.delete('/clear')
def clear_notifications(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id).delete()
    db.commit()

    return {"success": True}
