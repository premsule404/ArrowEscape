import json
import os
import sys
import random

sys.path.insert(0, os.path.dirname(__file__))

from shared.engine.level_parser import LevelParser
from shared.engine.solver import HintSystem
from shared.engine.models import Arrow, Position, Direction
from shared.engine.board import Board
from shared.engine.engine import GameEngine

def has_facing_pairs(placed_dict):
    """
    Checks if any two adjacent arrows point directly at each other.
    Facing right/left: arrow at (x, y) pointing RIGHT and arrow at (x+1, y) pointing LEFT.
    Facing up/down: arrow at (x, y) pointing DOWN and arrow at (x, y+1) pointing UP.
    """
    grid = {}
    for pos, arr_data in placed_dict.items():
        grid[pos] = arr_data["direction"]
        
    for (x, y), d in grid.items():
        if d == "RIGHT" and grid.get((x + 1, y)) == "LEFT":
            return True
        if d == "LEFT" and grid.get((x - 1, y)) == "RIGHT":
            return True
        if d == "DOWN" and grid.get((x, y + 1)) == "UP":
            return True
        if d == "UP" and grid.get((x, y - 1)) == "DOWN":
            return True
    return False

def generate_fullboard_layout(level_id, name, difficulty, width, height, num_arrows, base_coins, seed=100, randomize_colors=False, has_black_master=False, has_golden_master=False):
    """
    Generates a full-board puzzle layout distributed across the entire matrix (including heavy center usage)
    with irregular path lengths, mixed directions, zero facing pairs, optional Black Master Arrow, and verified 100% solvability.
    """
    color_palette = ["red", "blue", "green", "orange", "yellow", "purple", "cyan"]
    
    for current_seed in range(seed, seed + 2000):
        rng = random.Random(current_seed)
        placed = {} # (x, y) -> dict
        
        dirs_list = [("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0)]
        
        def is_ray_clear(x, y, dx, dy):
            cx, cy = x + dx, y + dy
            while 0 <= cx < width and 0 <= cy < height:
                if (cx, cy) in placed:
                    return False
                cx += dx
                cy += dy
            return True

        # Phase 1: Place initial escape arrows across center and middle cells pointing out
        all_cells = [(x, y) for x in range(width) for y in range(height)]
        def dist_to_border(pos):
            x, y = pos
            return min(x, width - 1 - x, y, height - 1 - y)
            
        all_cells.sort(key=dist_to_border, reverse=True)
        
        for x, y in all_cells:
            if len(placed) >= num_arrows:
                break
            shuffled_dirs = list(dirs_list)
            rng.shuffle(shuffled_dirs)
            for d_name, dx, dy in shuffled_dirs:
                if is_ray_clear(x, y, dx, dy):
                    placed[(x, y)] = {
                        "id": f"a{len(placed)+1}",
                        "x": x,
                        "y": y,
                        "direction": d_name,
                        "theme": rng.choice(color_palette) if randomize_colors else "default",
                        "is_black_master": False,
                        "is_golden_master": False
                    }
                    break

        # Phase 2: Grow dependency chains by placing blocking arrows across existing rays
        attempts = 0
        while len(placed) < num_arrows and attempts < 2500:
            attempts += 1
            if not placed:
                break
            target_pos = rng.choice(list(placed.keys()))
            target_arr = placed[target_pos]
            tdx, tdy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}[target_arr["direction"]]
            
            cx, cy = target_arr["x"] + tdx, target_arr["y"] + tdy
            ray_cells = []
            while 0 <= cx < width and 0 <= cy < height:
                if (cx, cy) not in placed:
                    ray_cells.append((cx, cy))
                else:
                    break
                cx += tdx
                cy += tdy
                
            if not ray_cells:
                continue
                
            bx, by = rng.choice(ray_cells)
            b_dirs = list(dirs_list)
            rng.shuffle(b_dirs)
            chosen_dname = b_dirs[0][0]
            
            placed[(bx, by)] = {
                "id": f"a{len(placed)+1}",
                "x": bx,
                "y": by,
                "direction": chosen_dname,
                "theme": rng.choice(color_palette) if randomize_colors else "default",
                "is_black_master": False,
                "is_golden_master": False
            }

        # Phase 3: Fill remaining grid slots
        remaining_slots = [(x, y) for x in range(width) for y in range(height) if (x, y) not in placed]
        rng.shuffle(remaining_slots)
        
        for x, y in remaining_slots:
            if len(placed) >= num_arrows:
                break
            b_dirs = list(dirs_list)
            rng.shuffle(b_dirs)
            placed[(x, y)] = {
                "id": f"a{len(placed)+1}",
                "x": x,
                "y": y,
                "direction": b_dirs[0][0],
                "theme": rng.choice(color_palette) if randomize_colors else "default",
                "is_black_master": False,
                "is_golden_master": False
            }
            
        if len(placed) < num_arrows:
            continue
            
        # MANDATORY CHECK: Enforce zero facing pairs
        if has_facing_pairs(placed):
            continue
            
        # Designate exactly ONE Black Master Arrow near strategic center
        if has_black_master or has_golden_master:
            center_x, center_y = width // 2, height // 2
            sorted_by_center = sorted(
                placed.keys(),
                key=lambda pos: (pos[0] - center_x) ** 2 + (pos[1] - center_y) ** 2
            )
            master_pos = sorted_by_center[0]
            if has_black_master:
                placed[master_pos]["theme"] = "black"
                placed[master_pos]["is_black_master"] = True
            elif has_golden_master:
                placed[master_pos]["theme"] = "gold"
                placed[master_pos]["is_golden_master"] = True

        arrows_list = []
        for idx, ((x, y), arr_data) in enumerate(placed.items(), 1):
            arr_data["id"] = f"a{idx}"
            arrows_list.append(arr_data)
            
        lvl_data = {
            "id": level_id,
            "name": name,
            "difficulty": difficulty,
            "grid": {"width": width, "height": height},
            "arrows": arrows_list,
            "rewards": {"coins": base_coins}
        }
        
        # Test solvability with HintSystem
        try:
            engine, meta = LevelParser.load_from_json(lvl_data)
            solver = HintSystem(engine)
            hint = solver.get_next_hint()
            if hint is not None:
                return lvl_data
        except Exception:
            pass
            
    raise RuntimeError(f"Could not generate solvable layout for {level_id}")

# Levels 1 to 40 (UNTOUCHED)
levels_data_1_to_40 = [
    # Level 1: "The Beginning" (4x4)
    {
        "id": "level001",
        "name": "Level 1: The Beginning",
        "difficulty": 1,
        "grid": {"width": 4, "height": 4},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 1, "y": 2, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 50}
    },
    # Level 2: "Crossroads" (4x4)
    {
        "id": "level002",
        "name": "Level 2: Crossroads",
        "difficulty": 1,
        "grid": {"width": 4, "height": 4},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 2, "y": 2, "direction": "DOWN", "theme": "default"},
            {"id": "a4", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"}
        ],
        "rewards": {"coins": 60}
    },
    # Level 3: "Winding Paths" (5x5)
    {
        "id": "level003",
        "name": "Level 3: Winding Paths",
        "difficulty": 2,
        "grid": {"width": 5, "height": 5},
        "arrows": [
            {"id": "a1", "x": 2, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a3", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a4", "x": 3, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a5", "x": 2, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a6", "x": 0, "y": 0, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 70}
    },
    # Level 4: "Traffic Jam" (5x5)
    {
        "id": "level004",
        "name": "Level 4: Traffic Jam",
        "difficulty": 2,
        "grid": {"width": 5, "height": 5},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a2", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a3", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 3, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a5", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a7", "x": 3, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a8", "x": 1, "y": 3, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 80}
    },
    # Level 5: "Spiral Escape" (6x6)
    {
        "id": "level005",
        "name": "Level 5: Spiral Escape",
        "difficulty": 3,
        "grid": {"width": 6, "height": 6},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a4", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 1, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 4, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a8", "x": 4, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a9", "x": 2, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 3, "y": 4, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 90}
    },
    # Level 6: "Interlock" (6x6)
    {
        "id": "level006",
        "name": "Level 6: Interlock",
        "difficulty": 3,
        "grid": {"width": 6, "height": 6},
        "arrows": [
            {"id": "a1", "x": 0, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 1, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 3, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a5", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a6", "x": 4, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 2, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a8", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 4, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 1, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a11", "x": 2, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a12", "x": 5, "y": 4, "direction": "UP", "theme": "default"}
        ],
        "rewards": {"coins": 100}
    },
    # Level 7: "Pinwheel" (6x6)
    {
        "id": "level007",
        "name": "Level 7: Pinwheel",
        "difficulty": 3,
        "grid": {"width": 6, "height": 6},
        "arrows": [
            {"id": "a1", "x": 2, "y": 1, "direction": "LEFT", "theme": "default"},
            {"id": "a2", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a4", "x": 4, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 1, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a6", "x": 4, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 2, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a8", "x": 3, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a9", "x": 0, "y": 0, "direction": "RIGHT", "theme": "default"},
            {"id": "a10", "x": 5, "y": 5, "direction": "LEFT", "theme": "default"}
        ],
        "rewards": {"coins": 110}
    },
    # Level 8: "Gridlock Gambit" (7x7)
    {
        "id": "level008",
        "name": "Level 8: Gridlock Gambit",
        "difficulty": 4,
        "grid": {"width": 7, "height": 7},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a6", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a7", "x": 2, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 4, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a9", "x": 5, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a10", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a11", "x": 2, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a12", "x": 3, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 4, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a14", "x": 5, "y": 5, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 120}
    },
    # Level 9: "Maze Master" (7x7)
    {
        "id": "level009",
        "name": "Level 9: Maze Master",
        "difficulty": 4,
        "grid": {"width": 7, "height": 7},
        "arrows": [
            {"id": "a1", "x": 2, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 3, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a3", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 1, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a6", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a7", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 4, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a9", "x": 1, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 5, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a11", "x": 2, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a12", "x": 3, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a13", "x": 4, "y": 5, "direction": "LEFT", "theme": "default"}
        ],
        "rewards": {"coins": 130}
    },
    # Level 10: "Grand Finale" (8x8)
    {
        "id": "level010",
        "name": "Level 10: Grand Finale",
        "difficulty": 5,
        "grid": {"width": 8, "height": 8},
        "arrows": [
            {"id": "a1", "x": 2, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 4, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a6", "x": 5, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 2, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a8", "x": 5, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a9", "x": 2, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a10", "x": 3, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a11", "x": 4, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a12", "x": 5, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a14", "x": 6, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 1, "y": 6, "direction": "UP", "theme": "default"},
            {"id": "a16", "x": 6, "y": 6, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 150}
    },
    # Level 11: "Zigzag Labyrinth" (8x8)
    {
        "id": "level011",
        "name": "Level 11: Zigzag Labyrinth",
        "difficulty": 5,
        "grid": {"width": 8, "height": 8},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a4", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a6", "x": 6, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a7", "x": 1, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 5, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 6, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a11", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a12", "x": 2, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 3, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a14", "x": 4, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 5, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a16", "x": 6, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a17", "x": 2, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a18", "x": 4, "y": 6, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 160}
    },
    # Level 12: "The Fortress" (8x8)
    {
        "id": "level012",
        "name": "Level 12: The Fortress",
        "difficulty": 6,
        "grid": {"width": 8, "height": 8},
        "arrows": [
            {"id": "a1", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a6", "x": 6, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a8", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 4, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 6, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a11", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a12", "x": 3, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 4, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a14", "x": 6, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a15", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a16", "x": 6, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a17", "x": 2, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a18", "x": 3, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a19", "x": 4, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a20", "x": 5, "y": 6, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 170}
    },
    # Level 13: "Clockwork Core" (9x9)
    {
        "id": "level013",
        "name": "Level 13: Clockwork Core",
        "difficulty": 6,
        "grid": {"width": 9, "height": 9},
        "arrows": [
            {"id": "a1", "x": 2, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 4, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 6, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a7", "x": 6, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a8", "x": 2, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a9", "x": 4, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 6, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a11", "x": 2, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a12", "x": 6, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a13", "x": 2, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a14", "x": 3, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 4, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a16", "x": 5, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a17", "x": 6, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a18", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a19", "x": 7, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a20", "x": 1, "y": 7, "direction": "UP", "theme": "default"},
            {"id": "a21", "x": 7, "y": 7, "direction": "RIGHT", "theme": "default"},
            {"id": "a22", "x": 4, "y": 1, "direction": "UP", "theme": "default"}
        ],
        "rewards": {"coins": 180}
    },
    # Level 14: "Tangled Web" (9x9)
    {
        "id": "level014",
        "name": "Level 14: Tangled Web",
        "difficulty": 7,
        "grid": {"width": 9, "height": 9},
        "arrows": [
            {"id": "a1", "x": 1, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a3", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 4, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a5", "x": 5, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 6, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a7", "x": 7, "y": 2, "direction": "DOWN", "theme": "default"},
            {"id": "a8", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a9", "x": 3, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 5, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a11", "x": 7, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a12", "x": 1, "y": 6, "direction": "UP", "theme": "default"},
            {"id": "a13", "x": 2, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a14", "x": 3, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 4, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a16", "x": 5, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a17", "x": 6, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a18", "x": 7, "y": 6, "direction": "DOWN", "theme": "default"},
            {"id": "a19", "x": 2, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a20", "x": 6, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a21", "x": 2, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a22", "x": 6, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 4, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a24", "x": 4, "y": 5, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 190}
    },
    # Level 15: "Crossfire Crisis" (9x9)
    {
        "id": "level015",
        "name": "Level 15: Crossfire Crisis",
        "difficulty": 7,
        "grid": {"width": 9, "height": 9},
        "arrows": [
            {"id": "a1", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 6, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a7", "x": 7, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a8", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a9", "x": 7, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a10", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a11", "x": 3, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a12", "x": 5, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 7, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a14", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a15", "x": 7, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a16", "x": 1, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a17", "x": 7, "y": 6, "direction": "RIGHT", "theme": "default"},
            {"id": "a18", "x": 2, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a19", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a20", "x": 4, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a21", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a22", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 0, "y": 0, "direction": "RIGHT", "theme": "default"},
            {"id": "a24", "x": 8, "y": 0, "direction": "DOWN", "theme": "default"},
            {"id": "a25", "x": 0, "y": 8, "direction": "UP", "theme": "default"},
            {"id": "a26", "x": 8, "y": 8, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 200}
    },
    # Level 16: "Chamber of Shadows" (9x9)
    {
        "id": "level016",
        "name": "Level 16: Chamber of Shadows",
        "difficulty": 8,
        "grid": {"width": 9, "height": 9},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 6, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 7, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a7", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a8", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a9", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a10", "x": 5, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a11", "x": 6, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a12", "x": 7, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a13", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a14", "x": 4, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a15", "x": 7, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a16", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a17", "x": 2, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a18", "x": 3, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a19", "x": 5, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a20", "x": 6, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a21", "x": 7, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a22", "x": 1, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 2, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a24", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a25", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a26", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a27", "x": 7, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a28", "x": 4, "y": 1, "direction": "UP", "theme": "default"}
        ],
        "rewards": {"coins": 210}
    },
    # Level 17: "Matrix of Confusion" (10x10)
    {
        "id": "level017",
        "name": "Level 17: Matrix of Confusion",
        "difficulty": 8,
        "grid": {"width": 10, "height": 10},
        "arrows": [
            {"id": "a1", "x": 2, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 4, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 5, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 6, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 7, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a7", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a8", "x": 7, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a9", "x": 2, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 4, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a11", "x": 5, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a12", "x": 7, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a13", "x": 2, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a14", "x": 4, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a15", "x": 5, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a16", "x": 7, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a17", "x": 2, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a18", "x": 7, "y": 6, "direction": "RIGHT", "theme": "default"},
            {"id": "a19", "x": 2, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a20", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a21", "x": 4, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a22", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a24", "x": 7, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a25", "x": 1, "y": 1, "direction": "RIGHT", "theme": "default"},
            {"id": "a26", "x": 8, "y": 1, "direction": "DOWN", "theme": "default"},
            {"id": "a27", "x": 1, "y": 8, "direction": "UP", "theme": "default"},
            {"id": "a28", "x": 8, "y": 8, "direction": "RIGHT", "theme": "default"},
            {"id": "a29", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a30", "x": 6, "y": 6, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 220}
    },
    # Level 18: "Knot Master" (10x10)
    {
        "id": "level018",
        "name": "Level 18: Knot Master",
        "difficulty": 9,
        "grid": {"width": 10, "height": 10},
        "arrows": [
            {"id": "a1", "x": 1, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 4, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 6, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a7", "x": 7, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 8, "y": 2, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 3, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a11", "x": 4, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a12", "x": 5, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a13", "x": 6, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a14", "x": 8, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a15", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a16", "x": 3, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a17", "x": 4, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a18", "x": 5, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a19", "x": 6, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a20", "x": 8, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a21", "x": 1, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a22", "x": 2, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a24", "x": 4, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a25", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a26", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a27", "x": 7, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a28", "x": 8, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a29", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a30", "x": 7, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a31", "x": 2, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a32", "x": 7, "y": 6, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 230}
    },
    # Level 19: "Infernal Gauntlet" (10x10)
    {
        "id": "level019",
        "name": "Level 19: Infernal Gauntlet",
        "difficulty": 9,
        "grid": {"width": 10, "height": 10},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 6, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a7", "x": 7, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 8, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 2, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a11", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a12", "x": 4, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a13", "x": 5, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a14", "x": 6, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 7, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a16", "x": 8, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a17", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a18", "x": 2, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a19", "x": 3, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a20", "x": 4, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a21", "x": 5, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a22", "x": 6, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a23", "x": 7, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a24", "x": 8, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a25", "x": 1, "y": 7, "direction": "LEFT", "theme": "default"},
            {"id": "a26", "x": 2, "y": 7, "direction": "LEFT", "theme": "default"},
            {"id": "a27", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a28", "x": 4, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a29", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a30", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a31", "x": 7, "y": 7, "direction": "RIGHT", "theme": "default"},
            {"id": "a32", "x": 8, "y": 7, "direction": "RIGHT", "theme": "default"},
            {"id": "a33", "x": 0, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a34", "x": 9, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a35", "x": 4, "y": 9, "direction": "RIGHT", "theme": "default"}
        ],
        "rewards": {"coins": 240}
    },
    # Level 20: "Ultimate Arrow Escape" (10x10)
    {
        "id": "level020",
        "name": "Level 20: Ultimate Arrow Escape",
        "difficulty": 10,
        "grid": {"width": 10, "height": 10},
        "arrows": [
            {"id": "a1", "x": 1, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a2", "x": 2, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a3", "x": 3, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a4", "x": 4, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a5", "x": 5, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a6", "x": 6, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a7", "x": 7, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a8", "x": 8, "y": 1, "direction": "UP", "theme": "default"},
            {"id": "a9", "x": 1, "y": 2, "direction": "LEFT", "theme": "default"},
            {"id": "a10", "x": 8, "y": 2, "direction": "RIGHT", "theme": "default"},
            {"id": "a11", "x": 1, "y": 3, "direction": "LEFT", "theme": "default"},
            {"id": "a12", "x": 3, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a13", "x": 4, "y": 3, "direction": "UP", "theme": "default"},
            {"id": "a14", "x": 5, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a15", "x": 6, "y": 3, "direction": "DOWN", "theme": "default"},
            {"id": "a16", "x": 8, "y": 3, "direction": "RIGHT", "theme": "default"},
            {"id": "a17", "x": 1, "y": 4, "direction": "LEFT", "theme": "default"},
            {"id": "a18", "x": 3, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a19", "x": 4, "y": 4, "direction": "UP", "theme": "default"},
            {"id": "a20", "x": 5, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a21", "x": 6, "y": 4, "direction": "DOWN", "theme": "default"},
            {"id": "a22", "x": 8, "y": 4, "direction": "RIGHT", "theme": "default"},
            {"id": "a23", "x": 1, "y": 5, "direction": "LEFT", "theme": "default"},
            {"id": "a24", "x": 3, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a25", "x": 4, "y": 5, "direction": "UP", "theme": "default"},
            {"id": "a26", "x": 5, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a27", "x": 6, "y": 5, "direction": "DOWN", "theme": "default"},
            {"id": "a28", "x": 8, "y": 5, "direction": "RIGHT", "theme": "default"},
            {"id": "a29", "x": 1, "y": 6, "direction": "LEFT", "theme": "default"},
            {"id": "a30", "x": 8, "y": 6, "direction": "RIGHT", "theme": "default"},
            {"id": "a31", "x": 1, "y": 7, "direction": "LEFT", "theme": "default"},
            {"id": "a32", "x": 3, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a33", "x": 4, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a34", "x": 5, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a35", "x": 6, "y": 7, "direction": "DOWN", "theme": "default"},
            {"id": "a36", "x": 8, "y": 7, "direction": "RIGHT", "theme": "default"},
            {"id": "a37", "x": 1, "y": 8, "direction": "DOWN", "theme": "default"},
            {"id": "a38", "x": 2, "y": 8, "direction": "DOWN", "theme": "default"},
            {"id": "a39", "x": 7, "y": 8, "direction": "DOWN", "theme": "default"},
            {"id": "a40", "x": 8, "y": 8, "direction": "DOWN", "theme": "default"}
        ],
        "rewards": {"coins": 250}
    },
    generate_fullboard_layout("level021", "Level 21: Hard Nexus", 10, 10, 10, 45, 260, seed=101),
    generate_fullboard_layout("level022", "Level 22: Vanguard Shield", 11, 11, 11, 52, 270, seed=102),
    generate_fullboard_layout("level023", "Level 23: Iron Citadel", 11, 11, 11, 60, 280, seed=103),
    generate_fullboard_layout("level024", "Level 24: Quantum Spiral", 12, 10, 10, 55, 290, seed=501),
    generate_fullboard_layout("level025", "Level 25: Titan Mesh", 12, 11, 11, 68, 300, seed=502),
    generate_fullboard_layout("level026", "Level 26: Nebula Crossfire", 13, 11, 11, 78, 310, seed=503),
    generate_fullboard_layout("level027", "Level 27: Omega Labyrinth", 13, 12, 12, 90, 320, seed=504),
    generate_fullboard_layout("level028", "Level 28: Eclipse Overlord", 14, 12, 12, 105, 330, seed=505),
    generate_fullboard_layout("level029", "Level 29: Apex Pinnacle", 14, 13, 13, 120, 340, seed=506),
    generate_fullboard_layout("level030", "Level 30: Grand Master Escape", 15, 13, 13, 140, 350, seed=507),
    generate_fullboard_layout("level031", "Level 31: Master Nexus", 16, 14, 14, 130, 360, seed=701, randomize_colors=True),
    generate_fullboard_layout("level032", "Level 32: Vanguard Fortress", 16, 14, 14, 145, 370, seed=702, randomize_colors=True),
    generate_fullboard_layout("level033", "Level 33: Iron Labyrinth", 17, 15, 15, 160, 380, seed=703, randomize_colors=True),
    generate_fullboard_layout("level034", "Level 34: Quantum Citadel", 17, 15, 15, 175, 390, seed=704, randomize_colors=True),
    generate_fullboard_layout("level035", "Level 35: Titan Mesh Core", 18, 16, 16, 190, 400, seed=705, randomize_colors=True),
    generate_fullboard_layout("level036", "Level 36: Nebula Crossfire II", 18, 16, 16, 205, 410, seed=706, randomize_colors=True),
    generate_fullboard_layout("level037", "Level 37: Omega Labyrinth II", 19, 17, 17, 220, 420, seed=707, randomize_colors=True),
    generate_fullboard_layout("level038", "Level 38: Eclipse Overlord II", 19, 17, 17, 235, 430, seed=708, randomize_colors=True),
    generate_fullboard_layout("level039", "Level 39: Apex Pinnacle II", 20, 18, 18, 250, 440, seed=709, randomize_colors=True),
    generate_fullboard_layout("level040", "Level 40: Ultimate Challenge", 20, 18, 18, 265, 450, seed=710, randomize_colors=True),
]

# ELITE LEVEL PACK: Levels 41 to 50 (Elite Series with Black Master Arrow)
levels_41_to_50 = [
    generate_fullboard_layout("level041", "Level 41: Elite Crossroads", 21, 15, 15, 160, 460, seed=901, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level042", "Level 42: Vanguard Core", 21, 15, 15, 175, 470, seed=902, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level043", "Level 43: Iron Nexus", 22, 16, 16, 190, 480, seed=903, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level044", "Level 44: Quantum Mesh", 22, 16, 16, 205, 490, seed=904, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level045", "Level 45: Titan Citadel", 23, 17, 17, 220, 500, seed=905, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level046", "Level 46: Nebula Overlord", 23, 17, 17, 235, 510, seed=906, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level047", "Level 47: Omega Gauntlet", 24, 18, 18, 250, 520, seed=907, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level048", "Level 48: Eclipse Pinnacle", 24, 18, 18, 265, 530, seed=908, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level049", "Level 49: Apex Master", 25, 18, 18, 280, 540, seed=909, randomize_colors=True, has_black_master=True),
    generate_fullboard_layout("level050", "Level 50: Final Elite Challenge", 25, 18, 18, 300, 550, seed=910, randomize_colors=True, has_black_master=True),
]

levels_data = levels_data_1_to_40 + levels_41_to_50

if __name__ == "__main__":
    os.makedirs("levels", exist_ok=True)
    all_ok = True
    metrics_41_50 = []
    
    for i, lvl in enumerate(levels_data, 1):
        filepath = f"levels/level{i:03d}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(lvl, f, indent=2)
        
        engine, meta = LevelParser.load_from_json(lvl)
        solver = HintSystem(engine)
        hint = solver.get_next_hint()
        
        init_valid = [aid for aid, a in engine.board.arrows.items() if engine.can_move(a)]
        
        bm_arrows = [a for a in lvl["arrows"] if a.get("is_black_master") or a.get("theme") == "black"]
        bm_pos_str = f"({bm_arrows[0]['x']}, {bm_arrows[0]['y']})" if bm_arrows else "None"
        
        is_solvable = hint is not None
        if not is_solvable:
            print(f"ERROR: {filepath} ({lvl['name']}) is NOT solvable!")
            all_ok = False
        else:
            print(f"SUCCESS: {filepath} ({lvl['name']}) verified solvable! ({len(lvl['arrows'])} arrows, Black Master: {bm_pos_str})")
            
        if 41 <= i <= 50:
            metrics_41_50.append({
                "level": i,
                "name": lvl["name"],
                "grid": f"{lvl['grid']['width']}x{lvl['grid']['height']}",
                "arrows": len(lvl['arrows']),
                "timer": f"{len(lvl['arrows'])}s",
                "bm_pos": bm_pos_str,
                "initial_moves": len(init_valid),
                "solvable": "YES" if is_solvable else "NO"
            })

    if all_ok:
        print("\nALL 50 LEVELS GENERATED AND VERIFIED SOLVABLE!")
        print("\n=== ELITE LEVEL PACK (LEVELS 41-50) METRICS REPORT ===")
        for m in metrics_41_50:
            print(f"Level {m['level']} ({m['name']}): Matrix {m['grid']} | Arrows: {m['arrows']} | Timer: {m['timer']} | Black Master Arrow: {m['bm_pos']} | Initial Moves: {m['initial_moves']} | Solvable: {m['solvable']}")
    else:
        sys.exit(1)
