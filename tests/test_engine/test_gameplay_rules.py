import pytest
import os
import json
from shared.engine.models import Arrow, Position, Direction
from shared.engine.engine import GameEngine
from shared.engine.constants import GameState, calculate_stars, calculate_allowed_level_time, calculate_coin_reward
from shared.engine.level_parser import LevelParser
from shared.engine.solver import HintSystem
from android.services.storage_service import StorageService

# 1. 3 stars -> 100% coins
def test_three_stars_gives_100_percent_coins():
    assert calculate_coin_reward(3, 100) == 100
    assert calculate_coin_reward(3, 220) == 220

# 2. 2 stars -> 70% coins
def test_two_stars_gives_70_percent_coins():
    assert calculate_coin_reward(2, 100) == 70
    assert calculate_coin_reward(2, 220) == 154

# 3. 1 star -> 50% coins
def test_one_star_gives_50_percent_coins():
    assert calculate_coin_reward(1, 100) == 50
    assert calculate_coin_reward(1, 220) == 110

# 4. 0 stars -> 0 coins
def test_zero_stars_gives_zero_coins():
    assert calculate_coin_reward(0, 100) == 0
    assert calculate_coin_reward(0, 220) == 0

# 5. Replay resets the current level correctly
def test_replay_resets_current_level_correctly():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(0.2)
    engine.tap_arrow("1")
    assert engine.state == GameState.COMPLETED
    
    engine.restart()
    assert engine.state == GameState.READY
    assert engine.hearts == 3
    assert engine.moves_count == 0
    assert engine.elapsed_time == 0.0
    assert engine.time_remaining == engine.total_time
    assert len(engine.board.arrows) == 1

# 6. Replay preserves previous best score
def test_replay_preserves_previous_best_score(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    res1 = store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    assert res1["best_stars"] == 3
    assert res1["best_time"] == 10.0
    
    res2 = store.save_level_progress(level_id=1, stars=1, moves=15, time=25.0, base_coins=100)
    assert res2["best_stars"] == 3
    assert res2["best_time"] == 10.0

# 7. Better replay updates best stars
def test_better_replay_updates_best_stars(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    res1 = store.save_level_progress(level_id=1, stars=2, moves=10, time=20.0, base_coins=100)
    assert res1["best_stars"] == 2
    
    res2 = store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    assert res2["best_stars"] == 3
    assert res2["is_new_best"] is True

# 8. Worse replay does not reduce best stars
def test_worse_replay_does_not_reduce_best_stars(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    res1 = store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    assert res1["best_stars"] == 3
    
    res2 = store.save_level_progress(level_id=1, stars=1, moves=15, time=25.0, base_coins=100)
    assert res2["best_stars"] == 3

# 9. Better replay awards only incremental coins
def test_better_replay_awards_only_incremental_coins(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    res1 = store.save_level_progress(level_id=1, stars=1, moves=10, time=22.0, base_coins=100)
    assert res1["earned_coins"] == 50
    assert res1["incremental_coins"] == 50
    assert res1["total_coins"] == 50
    
    res2 = store.save_level_progress(level_id=1, stars=2, moves=8, time=18.0, base_coins=100)
    assert res2["earned_coins"] == 70
    assert res2["incremental_coins"] == 20
    assert res2["total_coins"] == 70

# 10. Replaying after maximum reward gives 0 additional coins
def test_replaying_after_maximum_reward_gives_zero_additional_coins(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    res1 = store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    assert res1["incremental_coins"] == 100
    assert res1["total_coins"] == 100
    
    res2 = store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    assert res2["incremental_coins"] == 0
    assert res2["total_coins"] == 100

# 11. Heart HUD initially displays exactly 3 hearts
def test_heart_hud_initially_displays_3_hearts():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    assert engine.max_hearts == 3
    assert engine.hearts == 3

# 12. Wrong move removes exactly one heart
def test_wrong_move_removes_exactly_one_heart():
    engine = GameEngine()
    arrow1 = Arrow("1", Position(0, 0), Direction.RIGHT)
    arrow2 = Arrow("2", Position(1, 0), Direction.UP)
    engine.load_level(3, 3, [arrow1, arrow2])
    
    assert engine.tap_arrow("1") is False
    assert engine.hearts == 2

# 13. Pause button is functional
def test_pause_button_is_functional():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    
    assert engine.pause() is True
    assert engine.state == GameState.PAUSED
    assert engine.is_paused is True

# 14. Pause freezes timer
def test_pause_freezes_timer():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(0.2)
    engine.pause()
    
    engine.tick_timer(100.0)
    assert engine.elapsed_time == 0.2

# 15. Resume continues from the exact previous state
def test_resume_continues_from_exact_previous_state():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(0.2)
    engine.pause()
    engine.resume()
    
    assert engine.state == GameState.PLAYING
    engine.tick_timer(0.3)
    assert round(engine.elapsed_time, 2) == 0.5

# 16. Level Select displays best stars
def test_level_select_displays_best_stars(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    store.save_level_progress(level_id=1, stars=3, moves=5, time=10.0, base_coins=100)
    
    prog = store.get_level_progress(1)
    assert prog["completed"] is True
    assert prog["best_stars"] == 3

# --- REGRESSION TESTS ---

def test_reg_timer_starts_on_replay():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    
    engine.tap_arrow("1")
    assert engine.state == GameState.COMPLETED
    
    engine.restart()
    assert engine.state == GameState.READY
    assert engine.time_remaining == engine.total_time
    
    engine.tap_arrow("1")
    assert engine.state == GameState.COMPLETED

def test_reg_replay_five_times():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    
    for attempt in range(5):
        assert engine.state == GameState.READY
        assert engine.time_remaining == engine.total_time
        engine.tap_arrow("1")
        assert engine.state == GameState.COMPLETED
        engine.restart()

def test_reg_complete_replay_loop():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    
    engine.start_game()
    engine.tick_timer(0.2)
    engine.tap_arrow("1")
    assert engine.state == GameState.COMPLETED
    
    engine.restart()
    assert engine.elapsed_time == 0.0
    assert engine.time_remaining == engine.total_time

def test_reg_pause_resume_timer():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(0.3)
    engine.pause()
    assert engine.state == GameState.PAUSED
    engine.resume()
    assert engine.state == GameState.PLAYING

def test_reg_pause_restart_timer():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(0.3)
    engine.pause()
    engine.restart()
    
    assert engine.state == GameState.READY
    assert engine.elapsed_time == 0.0

def test_reg_complete_replay_pause_resume():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    
    engine.tap_arrow("1")
    assert engine.state == GameState.COMPLETED
    
    engine.restart()
    engine.start_game()
    engine.pause()
    assert engine.state == GameState.PAUSED
    engine.resume()
    assert engine.state == GameState.PLAYING

def test_reg_fail_retry():
    engine = GameEngine()
    arrow = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow])
    engine.start_game()
    
    engine.tick_timer(100.0)
    assert engine.state == GameState.FAILED
    
    engine.restart()
    assert engine.state == GameState.READY
    assert engine.time_remaining == engine.total_time

def test_reg_total_allowed_time_equals_arrow_count():
    for i in range(1, 51):
        filepath = f"levels/level{i:03d}.json"
        assert os.path.exists(filepath), f"{filepath} missing!"
        engine, meta = LevelParser.load_from_file(filepath)
        assert engine.total_time == float(engine.total_arrows_count)

def test_reg_levels_41_to_50_are_solvable():
    for i in range(41, 51):
        filepath = f"levels/level{i:03d}.json"
        assert os.path.exists(filepath), f"{filepath} missing!"
        engine, meta = LevelParser.load_from_file(filepath)
        solver = HintSystem(engine)
        hint = solver.get_next_hint()
        assert hint is not None, f"Level {i} is NOT solvable!"

def test_reg_levels_41_to_50_have_exactly_one_black_master():
    for i in range(41, 51):
        filepath = f"levels/level{i:03d}.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        bm_count = sum(1 for a in data["arrows"] if a.get("is_black_master") or a.get("theme") == "black")
        assert bm_count == 1, f"Level {i} has {bm_count} Black Master arrows! Expected exactly 1."

def test_reg_no_facing_pairs_in_levels_41_to_50():
    for i in range(41, 51):
        filepath = f"levels/level{i:03d}.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        grid = {(a["x"], a["y"]): a["direction"] for a in data["arrows"]}
        for (x, y), d in grid.items():
            if d == "RIGHT": assert grid.get((x + 1, y)) != "LEFT", f"Facing pair in level {i} at ({x},{y})"
            if d == "LEFT": assert grid.get((x - 1, y)) != "RIGHT", f"Facing pair in level {i} at ({x},{y})"
            if d == "DOWN": assert grid.get((x, y + 1)) != "UP", f"Facing pair in level {i} at ({x},{y})"
            if d == "UP": assert grid.get((x, y - 1)) != "DOWN", f"Facing pair in level {i} at ({x},{y})"

def test_reg_max_available_stars_is_150(tmp_path):
    store = StorageService(filename=str(tmp_path / "test_store.json"))
    summary = store.get_player_summary(total_levels=50)
    assert summary["max_stars"] == 150
    assert summary["total_levels"] == 50
