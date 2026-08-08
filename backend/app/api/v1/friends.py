from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary
from ...models.social import Friend, FriendRequest
from ...api.v1.auth import require_current_user

router = APIRouter()

class FriendRequestPayload(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None

class ActionRequestPayload(BaseModel):
    request_id: int

class ChallengePayload(BaseModel):
    friend_id: int
    level_num: int = 1

def build_player_dict(user: User, profile: Optional[PlayerProfile], summary: Optional[UserProgressSummary], is_online: bool = True) -> Dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": profile.display_name if profile else user.username,
        "avatar": profile.avatar if profile else "🎯",
        "country": profile.country if profile else "Global",
        "is_online": is_online,
        "total_stars": summary.total_stars if summary else 0,
        "total_coins": summary.total_coins if summary else 0,
        "completed_levels": summary.completed_levels if summary else 0,
        "highest_level": summary.highest_unlocked_level if summary else 1
    }

@router.get('', response_model=Dict[str, Any])
def get_friends_data(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    # Fetch friends
    friend_relations = db.query(Friend).filter(or_(Friend.user_id == user.id, Friend.friend_id == user.id)).all()
    friend_ids = [f.friend_id if f.user_id == user.id else f.user_id for f in friend_relations]
    
    friends_users = db.query(User).filter(User.id.in_(friend_ids)).all() if friend_ids else []
    
    friends_list = []
    for f_user in friends_users:
        prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == f_user.id).first()
        summ = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == f_user.id).first()
        friends_list.append(build_player_dict(f_user, prof, summ, is_online=True))

    # Fetch pending incoming requests
    pending_reqs = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == user.id,
        FriendRequest.status == "pending"
    ).all()

    requests_list = []
    for req in pending_reqs:
        sender_user = db.query(User).filter(User.id == req.sender_id).first()
        if sender_user:
            prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == sender_user.id).first()
            summ = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == sender_user.id).first()
            requests_list.append({
                "request_id": req.id,
                "sender": build_player_dict(sender_user, prof, summ)
            })

    # Recently played (other users on leaderboard)
    recent_users = db.query(User).filter(User.id != user.id, ~User.id.in_(friend_ids)).limit(5).all() if friend_ids else db.query(User).filter(User.id != user.id).limit(5).all()
    recently_played = []
    for r_user in recent_users:
        prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == r_user.id).first()
        summ = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == r_user.id).first()
        recently_played.append(build_player_dict(r_user, prof, summ, is_online=False))

    return {
        "friends": friends_list,
        "pending_requests": requests_list,
        "recently_played": recently_played,
        "invite_link": f"https://arrowescape.onrender.com/?invite={user.id}"
    }

@router.get('/search', response_model=List[Dict[str, Any]])
def search_players(query: str = Query(..., min_length=1), user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    matched_users = db.query(User).filter(
        User.id != user.id,
        or_(User.username.ilike(f"%{query}%"), User.email.ilike(f"%{query}%"))
    ).limit(10).all()

    # Also search by display_name in PlayerProfile
    profile_matches = db.query(PlayerProfile).filter(PlayerProfile.display_name.ilike(f"%{query}%")).limit(10).all()
    profile_user_ids = [p.user_id for p in profile_matches if p.user_id != user.id]
    
    if profile_user_ids:
        additional_users = db.query(User).filter(User.id.in_(profile_user_ids), ~User.id.in_([u.id for u in matched_users])).all()
        matched_users.extend(additional_users)

    results = []
    for m_user in matched_users:
        prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == m_user.id).first()
        summ = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == m_user.id).first()
        
        # Check relation status
        is_friend = db.query(Friend).filter(
            or_(
                and_(Friend.user_id == user.id, Friend.friend_id == m_user.id),
                and_(Friend.user_id == m_user.id, Friend.friend_id == user.id)
            )
        ).first() is not None

        has_pending = db.query(FriendRequest).filter(
            FriendRequest.sender_id == user.id,
            FriendRequest.receiver_id == m_user.id,
            FriendRequest.status == "pending"
        ).first() is not None

        p_dict = build_player_dict(m_user, prof, summ)
        p_dict["is_friend"] = is_friend
        p_dict["has_pending_request"] = has_pending
        results.append(p_dict)

    return results

from datetime import datetime
from ...models.notifications import Notification

@router.post('/request')
def send_friend_request(payload: FriendRequestPayload, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    target_user = None
    if payload.user_id:
        target_user = db.query(User).filter(User.id == payload.user_id).first()
    elif payload.username:
        target_user = db.query(User).filter(User.username == payload.username).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target player not found.")

    if target_user.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself.")

    # Check if already friends
    existing_friend = db.query(Friend).filter(
        or_(
            and_(Friend.user_id == user.id, Friend.friend_id == target_user.id),
            and_(Friend.user_id == target_user.id, Friend.friend_id == user.id)
        )
    ).first()
    if existing_friend:
        raise HTTPException(status_code=400, detail="Player is already in your friends list.")

    # Check existing pending request
    existing_req = db.query(FriendRequest).filter(
        FriendRequest.sender_id == user.id,
        FriendRequest.receiver_id == target_user.id,
        FriendRequest.status == "pending"
    ).first()

    if existing_req:
        raise HTTPException(status_code=400, detail="Friend request already sent.")

    req = FriendRequest(sender_id=user.id, receiver_id=target_user.id, status="pending")
    db.add(req)
    
    # Notify target user
    notif = Notification(
        user_id=target_user.id,
        type="friend",
        title="Friend Request 📩",
        content=f"{user.username} sent you a friend request!",
        icon="👥",
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()

    return {"success": True, "message": f"Friend request sent to {target_user.username}!"}

@router.post('/accept')
def accept_friend_request(payload: ActionRequestPayload, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    req = db.query(FriendRequest).filter(FriendRequest.id == payload.request_id, FriendRequest.receiver_id == user.id).first()
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="Pending friend request not found.")

    req.status = "accepted"
    db.add(Friend(user_id=req.sender_id, friend_id=user.id))
    
    # Notify sender user
    notif = Notification(
        user_id=req.sender_id,
        type="friend",
        title="Friend Request Accepted 🎉",
        content=f"{user.username} accepted your friend request!",
        icon="👥",
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()

    return {"success": True, "message": "Friend request accepted!"}

@router.post('/reject')
def reject_friend_request(payload: ActionRequestPayload, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    req = db.query(FriendRequest).filter(FriendRequest.id == payload.request_id, FriendRequest.receiver_id == user.id).first()
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="Pending friend request not found.")

    req.status = "rejected"
    db.commit()

    return {"success": True, "message": "Friend request rejected."}

@router.delete('/{friend_id}')
def remove_friend(friend_id: int, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    relation = db.query(Friend).filter(
        or_(
            and_(Friend.user_id == user.id, Friend.friend_id == friend_id),
            and_(Friend.user_id == friend_id, Friend.friend_id == user.id)
        )
    ).first()

    if not relation:
        raise HTTPException(status_code=404, detail="Friend relationship not found.")

    db.delete(relation)
    db.commit()

    return {"success": True, "message": "Friend removed."}

@router.post('/challenge')
def challenge_friend(payload: ChallengePayload, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    friend_user = db.query(User).filter(User.id == payload.friend_id).first()
    if not friend_user:
        raise HTTPException(status_code=404, detail="Friend not found.")

    # Notify friend user
    notif = Notification(
        user_id=friend_user.id,
        type="challenge",
        title="Level Challenge! ⚔️",
        content=f"{user.username} challenged you to clear Level {payload.level_num}!",
        icon="⚔️",
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "message": f"Challenge sent to {friend_user.username} for Level {payload.level_num}!"
    }

@router.get('/profile/{user_id}', response_model=Dict[str, Any])
def get_friend_profile(user_id: int, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Player profile not found.")

    prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == user_id).first()
    summ = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user_id).first()

    return {
        "id": target_user.id,
        "username": target_user.username,
        "display_name": prof.display_name if prof else target_user.username,
        "avatar": prof.avatar if prof else "🎯",
        "country": prof.country if prof else "Global",
        "total_stars": summ.total_stars if summ else 0,
        "total_coins": summ.total_coins if summ else 0,
        "completed_levels": summ.completed_levels if summ else 0,
        "highest_level": summ.highest_unlocked_level if summ else 1,
        "best_score": summ.best_score if summ else 0,
        "date_joined": target_user.created_at.strftime("%Y-%m-%d") if hasattr(target_user, "created_at") and target_user.created_at else "2026-08-01"
    }
