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

def test_config_api():
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert data["total_levels"] == 50
    assert data["max_stars"] == 150

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
    
    # Cloud Save Sync (Highest Progress Wins)
    sync_payload = {
        "levels": [
            {"level_id": 1, "stars": 3, "moves": 5, "time": 12.5, "base_coins": 100, "completed": True}
        ],
        "current_level": 2
    }
    res_sync = client.post("/api/v1/cloud/sync", json=sync_payload, headers=headers)
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data["total_coins"] == 100
    assert sync_data["total_stars"] == 3
    assert sync_data["completed_count"] == 1

def test_profile_stats_and_settings_endpoints():
    res = client.post("/api/v1/auth/guest", json={"display_name": "Profile Tester"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Profile GET & PATCH
    prof_res = client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    
    patch_prof = client.patch("/api/v1/profile", json={"country": "India", "theme": "dark"}, headers=headers)
    assert patch_prof.status_code == 200
    assert patch_prof.json()["profile"]["country"] == "India"
    
    # Stats GET & PATCH
    stats_res = client.get("/api/v1/stats", headers=headers)
    assert stats_res.status_code == 200
    
    patch_stats = client.patch("/api/v1/stats", json={"games_played": 10}, headers=headers)
    assert patch_stats.status_code == 200
    
    # Settings GET & PATCH
    set_res = client.get("/api/v1/settings", headers=headers)
    assert set_res.status_code == 200
    
    patch_set = client.patch("/api/v1/settings", json={"music_volume": 0.5, "fps_limit": 120}, headers=headers)
    assert patch_set.status_code == 200
    assert patch_set.json()["settings"]["fps_limit"] == 120

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
    
    # Sync Level 1 & 2
    client.post("/api/v1/cloud/sync", json={
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

def test_official_levels_api():
    res = client.get("/api/v1/levels")
    assert res.status_code == 200
    levels = res.json()
    assert len(levels) == 50
    
    single_res = client.get("/api/v1/levels/1")
    assert single_res.status_code == 200
    single_lvl = single_res.json()
    assert single_lvl["id"] == "level001"

def test_404_error_formatting():
    res = client.get("/api/v1/levels/999")
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
