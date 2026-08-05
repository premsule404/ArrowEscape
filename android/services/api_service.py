import json
import urllib.request
import urllib.error

class ApiService:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url

    def _request(self, endpoint: str, method: str = "GET", data: dict = None, token: str = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        req_body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode("utf-8")
                return json.loads(res_data) if res_data else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"HTTP {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Network error: {str(e)}")

    def login(self, username, password) -> dict:
        return self._request("/auth/login", method="POST", data={"username": username, "password": password})

    def register(self, username, password, email=None) -> dict:
        return self._request("/auth/register", method="POST", data={"username": username, "password": password, "email": email})

    def cloud_save(self, level_id: int, stars: int, moves: int, time: float, token: str) -> dict:
        return self._request(
            "/progress/cloud-save",
            method="POST",
            data={"level_id": level_id, "stars": stars, "best_moves": moves, "best_time": time},
            token=token
        )
