import os
import sys
from kivy.storage.jsonstore import JsonStore

# Ensure shared engine constants can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.engine.constants import calculate_coin_reward

class StorageService:
    def __init__(self, filename="game_storage.json"):
        store_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        self.store = JsonStore(store_path)

    def set_token(self, token: str):
        self.store.put('auth', token=token)

    def get_token(self) -> str:
        if self.store.exists('auth'):
            return self.store.get('auth').get('token', '')
        return ''

    def clear_token(self):
        if self.store.exists('auth'):
            self.store.delete('auth')

    def get_total_coins(self) -> int:
        if self.store.exists('player_wallet'):
            return self.store.get('player_wallet').get('coins', 0)
        return 0

    def add_coins(self, amount: int) -> int:
        current = self.get_total_coins()
        updated = current + max(0, amount)
        self.store.put('player_wallet', coins=updated)
        return updated

    def save_level_progress(self, level_id: int, stars: int, moves: int, time: float, base_coins: int = 100) -> dict:
        key = f"level_{level_id}"
        existing = self.get_level_progress(level_id)
        
        prev_stars = existing.get('best_stars', 0)
        prev_time = existing.get('best_time', 0.0)
        prev_unlocked = existing.get('unlocked_coins', 0)
        attempt_count = existing.get('attempt_count', 0) + 1
        
        # Calculate new best records (ensure valid time > 0.0)
        valid_time = max(0.1, round(float(time), 2))
        best_stars = max(stars, prev_stars)
        best_moves = min(moves, existing['best_moves']) if existing.get('best_moves', 0) > 0 else moves
        
        if prev_time > 0.0:
            best_time = min(valid_time, prev_time)
            is_new_best = (stars > prev_stars) or (valid_time < prev_time)
        else:
            best_time = valid_time
            is_new_best = True
        
        # Incremental Coin Reward Policy (No farming)
        current_run_earned = calculate_coin_reward(stars, base_coins)
        incremental_coins = max(0, current_run_earned - prev_unlocked)
        new_unlocked = max(prev_unlocked, current_run_earned)
        
        if incremental_coins > 0:
            self.add_coins(incremental_coins)
            
        self.store.put(
            key,
            completed=True,
            best_stars=best_stars,
            best_moves=best_moves,
            best_time=best_time,
            unlocked_coins=new_unlocked,
            attempt_count=attempt_count
        )
        
        return {
            "is_new_best": is_new_best,
            "stars": stars,
            "best_stars": best_stars,
            "time": valid_time,
            "best_time": best_time,
            "earned_coins": current_run_earned,
            "incremental_coins": incremental_coins,
            "unlocked_coins": new_unlocked,
            "base_coins": base_coins,
            "total_coins": self.get_total_coins()
        }

    def get_level_progress(self, level_id: int) -> dict:
        key = f"level_{level_id}"
        if self.store.exists(key):
            res = self.store.get(key)
            return {
                "completed": res.get("completed", False),
                "best_stars": res.get("best_stars", res.get("stars", 0)),
                "best_moves": res.get("best_moves", 0),
                "best_time": float(res.get("best_time", 0.0)),
                "unlocked_coins": res.get("unlocked_coins", 0),
                "attempt_count": res.get("attempt_count", 0)
            }
        return {
            "completed": False,
            "best_stars": 0,
            "best_moves": 0,
            "best_time": 0.0,
            "unlocked_coins": 0,
            "attempt_count": 0
        }

    def get_player_summary(self, total_levels: int = 20) -> dict:
        total_stars = 0
        completed_count = 0
        
        for i in range(1, total_levels + 1):
            prog = self.get_level_progress(i)
            if prog["completed"]:
                completed_count += 1
                total_stars += prog["best_stars"]
                
        return {
            "total_stars": total_stars,
            "max_stars": total_levels * 3,
            "total_coins": self.get_total_coins(),
            "completed_count": completed_count,
            "total_levels": total_levels
        }

    def set_setting(self, key: str, value):
        self.store.put(f"setting_{key}", value=value)

    def get_setting(self, key: str, default=None):
        storage_key = f"setting_{key}"
        if self.store.exists(storage_key):
            return self.store.get(storage_key).get('value', default)
        return default
