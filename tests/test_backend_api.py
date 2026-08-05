import pytest
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_guest_login_and_sync():
    res = client.post("/api/v1/auth/guest", json={"display_name": "Test Player"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    token = data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Profile
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["is_guest"] is True
    assert me_data["display_name"] == "Test Player"
    
    # Cloud Save Sync (Simulate completing Level 1 with 3 stars)
    sync_payload = {
        "levels": [
            {"level_id": 1, "stars": 3, "moves": 5, "time": 12.5, "base_coins": 100, "completed": True}
        ],
        "current_level": 2
    }
    res_sync = client.post("/api/v1/progress/sync", json=sync_payload, headers=headers)
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data["total_coins"] == 100
    assert sync_data["total_stars"] == 3
    assert sync_data["completed_count"] == 1
    assert sync_data["highest_unlocked_level"] == 2

def test_user_register_login_and_leaderboard():
    uid = uuid.uuid4().hex[:6]
    uname = f"champ_{uid}"
    email = f"champ_{uid}@example.com"
    
    reg_res = client.post("/api/v1/auth/register", json={
        "username": uname,
        "email": email,
        "password": "secretpassword"
    })
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Complete Level 1 & 2
    client.post("/api/v1/progress/sync", json={
        "levels": [
            {"level_id": 1, "stars": 3, "moves": 5, "time": 10.0, "base_coins": 100, "completed": True},
            {"level_id": 2, "stars": 3, "moves": 8, "time": 15.0, "base_coins": 100, "completed": True}
        ]
    }, headers=headers)
    
    # Check Leaderboard
    lb_res = client.get("/api/v1/leaderboard?category=stars")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    assert len(lb_data) > 0
    assert lb_data[0]["total_stars"] >= 6

def test_official_levels_api():
    res = client.get("/api/v1/levels")
    assert res.status_code == 200
    levels = res.json()
    assert len(levels) == 50
    assert levels[0]["level_num"] == 1
    assert levels[49]["level_num"] == 50
