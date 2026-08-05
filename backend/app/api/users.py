from fastapi import APIRouter
from ..schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile():
    # Mock response
    return {
        "id": 1,
        "username": "Player1",
        "is_guest": False,
        "coins": 150,
        "stars": 12
    }
