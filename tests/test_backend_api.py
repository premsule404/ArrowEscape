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

def test_guest_account_upgrade_and_progress_merging():
    # 1. Create Guest Account & play level 1 & 2
    guest_res = client.post("/api/v1/auth/guest", json={"display_name": "Pro Guest"})
    guest_data = guest_res.json()
    token = guest_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    sync_res = client.post("/api/v1/cloud/sync", json={
        "levels": [
            {"level_id": 1, "stars": 3, "moves": 5, "time": 10.0, "base_coins": 100, "completed": True},
            {"level_id": 2, "stars": 3, "moves": 7, "time": 14.0, "base_coins": 100, "completed": True}
        ]
    }, headers=headers)
    assert sync_res.json()["total_coins"] == 200
    
    # 2. Upgrade Guest Account
    uid = uuid.uuid4().hex[:6]
    upg_res = client.post("/api/v1/auth/upgrade-guest", json={
        "username": f"permanent_{uid}",
        "password": "strongpassword123",
        "email": f"perm_{uid}@example.com"
    }, headers=headers)
    assert upg_res.status_code == 200
    upg_data = upg_res.json()
    assert upg_data["is_guest"] is False
    
    # 3. Verify progress was preserved
    new_token = upg_data["access_token"]
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["is_guest"] is False

def test_jwt_refresh_and_session_revocation():
    guest_res = client.post("/api/v1/auth/guest", json={"display_name": "Session Player"})
    assert guest_res.status_code == 200
    data = guest_res.json()
    ref_token = data["refresh_token"]
    acc_token = data["access_token"]
    headers = {"Authorization": f"Bearer {acc_token}"}
    
    # Refresh token
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()
    
    # Logout
    log_res = client.post("/api/v1/auth/logout", json={"refresh_token": ref_token})
    assert log_res.status_code == 200
    
    # Sessions
    sess_res = client.get("/api/v1/auth/sessions", headers=headers)
    assert sess_res.status_code == 200

def test_inventory_transactions_sync_status_and_admin():
    # Admin User
    admin_login = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Regular User
    reg_user = client.post("/api/v1/auth/guest", json={"display_name": "Economy Player"})
    user_token = reg_user.json()["access_token"]
    user_id = reg_user.json()["user_id"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 1. Admin Grants Coins
    grant_res = client.post(f"/api/v1/admin/users/{user_id}/grant-coins", json={"amount": 500}, headers=admin_headers)
    assert grant_res.status_code == 200
    assert grant_res.json()["new_balance"] == 500
    
    # 2. Check Inventory
    inv_res = client.get("/api/v1/inventory", headers=user_headers)
    assert inv_res.status_code == 200
    inv_items = inv_res.json()
    coin_item = next((i for i in inv_items if i["item_type"] == "coins"), None)
    assert coin_item["quantity"] == 500
    
    # 3. Check Transactions History
    tx_res = client.get("/api/v1/transactions", headers=user_headers)
    assert tx_res.status_code == 200
    tx_list = tx_res.json()
    assert len(tx_list) >= 1
    assert tx_list[0]["amount"] == 500
    
    # 4. Check Sync Status
    sync_status = client.get("/api/v1/sync/status", headers=user_headers)
    assert sync_status.status_code == 200
    assert sync_status.json()["sync_status"] == "UP_TO_DATE"

def test_new_account_isolation_and_level1_start():
    # 1. User A Register & Play
    u_a_id = uuid.uuid4().hex[:6]
    u_a_name = f"userA_{u_a_id}"
    res_a = client.post("/api/v1/auth/register", json={"username": u_a_name, "password": "password123"})
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify User A starts at Level 1 with 0 coins
    prog_a_init = client.get("/api/v1/progress", headers=headers_a).json()
    assert prog_a_init["current_level"] == 1
    assert prog_a_init["total_coins"] == 0
    assert prog_a_init["total_stars"] == 0
    assert len(prog_a_init["levels"]) == 0

    # User A completes Level 1 & 2
    client.post("/api/v1/cloud/sync", json={
        "levels": [
            {"level_id": 1, "stars": 3, "moves": 5, "time": 10.0, "base_coins": 100, "completed": True},
            {"level_id": 2, "stars": 3, "moves": 7, "time": 12.0, "base_coins": 100, "completed": True}
        ],
        "current_level": 3
    }, headers=headers_a)

    prog_a_after = client.get("/api/v1/progress", headers=headers_a).json()
    assert prog_a_after["total_coins"] == 200
    assert prog_a_after["current_level"] == 3

    # 2. User B Register
    u_b_id = uuid.uuid4().hex[:6]
    u_b_name = f"userB_{u_b_id}"
    res_b = client.post("/api/v1/auth/register", json={"username": u_b_name, "password": "password123"})
    assert res_b.status_code == 200
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Verify User B starts at Level 1 (NOT Level 3) with 0 coins (Isolation)
    prog_b_init = client.get("/api/v1/progress", headers=headers_b).json()
    assert prog_b_init["current_level"] == 1
    assert prog_b_init["total_coins"] == 0
    assert len(prog_b_init["levels"]) == 0

    # 3. User A sends friend request to User B
    req_res = client.post("/api/v1/friends/request", json={"username": u_b_name}, headers=headers_a)
    assert req_res.status_code == 200

    # 4. User B checks Notifications and sees Friend Request
    notif_b = client.get("/api/v1/notifications", headers=headers_b).json()
    assert notif_b["unread_count"] >= 1
    friend_notif = next((n for n in notif_b["notifications"] if n["type"] == "friend"), None)
    assert friend_notif is not None

    # 5. User B accepts Friend Request
    friends_b_data = client.get("/api/v1/friends", headers=headers_b).json()
    req_id = friends_b_data["pending_requests"][0]["request_id"]
    acc_res = client.post("/api/v1/friends/accept", json={"request_id": req_id}, headers=headers_b)
    assert acc_res.status_code == 200

    # 6. User A checks Friends list and sees User B
    friends_a_data = client.get("/api/v1/friends", headers=headers_a).json()
    friend_b_obj = next((f for f in friends_a_data["friends"] if f["username"] == u_b_name), None)
    assert friend_b_obj is not None

    # 7. User A challenges User B to Level 2
    chal_res = client.post("/api/v1/friends/challenge", json={"friend_id": friend_b_obj["id"], "level_num": 2}, headers=headers_a)
    assert chal_res.status_code == 200

    # 8. User B receives challenge notification
    notif_b2 = client.get("/api/v1/notifications", headers=headers_b).json()
    chal_notif = next((n for n in notif_b2["notifications"] if n["type"] == "challenge"), None)
    assert chal_notif is not None
