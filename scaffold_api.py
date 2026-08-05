import os

routes = {
    "auth": [("post", "register"), ("post", "login"), ("post", "logout"), ("post", "refresh"), ("post", "forgot-password"), ("post", "reset-password"), ("post", "verify-email"), ("get", "me")],
    "users": [("get", "profile"), ("put", "profile"), ("put", "avatar"), ("delete", "account")],
    "game": [("get", "config"), ("get", "settings"), ("put", "settings"), ("post", "start"), ("post", "pause"), ("post", "resume"), ("post", "finish")],
    "levels": [("get", ""), ("get", "{id}"), ("post", "{id}/start"), ("post", "{id}/complete"), ("post", "{id}/restart"), ("post", "{id}/hint"), ("post", "{id}/undo")],
    "progress": [("get", ""), ("put", ""), ("get", "statistics"), ("post", "cloud-save"), ("get", "cloud-load")],
    "achievements": [("get", ""), ("post", "unlock")],
    "coins": [("get", ""), ("post", "reward"), ("post", "spend")],
    "themes": [("get", ""), ("post", "unlock"), ("put", "equip")],
    "leaderboard": [("get", "global"), ("get", "friends"), ("get", "weekly"), ("get", "monthly")],
    "daily": [("get", ""), ("post", "claim")],
    "shop": [("get", "items"), ("post", "purchase")],
    "stats": [("get", ""), ("get", "history")],
    "notifications": [("get", ""), ("put", "read")],
    "admin": [("get", "dashboard"), ("get", "users"), ("get", "analytics"), ("post", "levels"), ("put", "levels/{id}"), ("delete", "levels/{id}")],
    "health": [("get", "")]
}

os.makedirs("backend/app/api/v1", exist_ok=True)
with open("backend/app/api/v1/__init__.py", "w") as f:
    pass

for module, endpoints in routes.items():
    with open(f"backend/app/api/v1/{module}.py", "w") as f:
        f.write("from fastapi import APIRouter\n\n")
        f.write("router = APIRouter()\n\n")
        for method, ep in endpoints:
            ep_path = f"/{ep}" if ep else "/"
            func_name = f"{method}_{ep.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_') or 'root'}"
            f.write(f"@router.{method}('{ep_path}')\n")
            f.write(f"def {func_name}():\n")
            f.write(f"    return {{'message': 'Mock response for {module} {ep_path}'}}\n\n")

print("API scaffolding complete.")
