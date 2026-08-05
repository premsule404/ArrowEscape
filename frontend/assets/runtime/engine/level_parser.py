import json
from typing import Tuple, Dict, Any
from dataclasses import dataclass
from .models import Arrow, Position, Direction
from .engine import GameEngine

@dataclass
class LevelMetadata:
    id: str
    name: str
    difficulty: int
    rewards: Dict[str, Any]

class LevelParser:
    @staticmethod
    def load_from_json(json_data: dict) -> Tuple[GameEngine, LevelMetadata]:
        # Parse metadata
        metadata = LevelMetadata(
            id=json_data.get("id", "unknown"),
            name=json_data.get("name", "Unknown Level"),
            difficulty=json_data.get("difficulty", 1),
            rewards=json_data.get("rewards", {})
        )
        
        # Parse grid
        grid_data = json_data.get("grid", {})
        width = grid_data.get("width", 5)
        height = grid_data.get("height", 5)
        
        # Parse arrows
        arrows_data = json_data.get("arrows", [])
        if not arrows_data and "paths" in json_data:
            paths_data = json_data.get("paths", [])
            arrows_data = []
            for p in paths_data:
                segments = p.get("segments", [])
                if segments:
                    arrows_data.append({
                        "id": p.get("id", "a0"),
                        "x": segments[0][0],
                        "y": segments[0][1],
                        "direction": p.get("direction", "UP"),
                        "theme": p.get("theme", "default"),
                        "is_black_master": p.get("is_black_master", False),
                        "is_golden_master": p.get("is_golden_master", False)
                    })
        arrows = []
        for a_data in arrows_data:
            direction_str = a_data.get("direction", "UP").upper()
            try:
                direction = Direction[direction_str]
            except KeyError:
                direction = Direction.UP
                
            theme_val = a_data.get("theme", "default")
            is_black = a_data.get("is_black_master", False) or (theme_val == "black")
            is_gold = a_data.get("is_golden_master", False) or (theme_val == "gold")
            
            arrow = Arrow(
                id=a_data.get("id", "a0"),
                position=Position(x=a_data.get("x", 0), y=a_data.get("y", 0)),
                direction=direction,
                color_theme="black" if is_black else ("gold" if is_gold else theme_val),
                is_black_master=is_black,
                is_golden_master=is_gold
            )
            # Validation: ensure bounds
            if not (0 <= arrow.position.x < width and 0 <= arrow.position.y < height):
                raise ValueError(f"Arrow {arrow.id} is placed out of grid bounds.")
                
            arrows.append(arrow)
            
        # Initialize engine
        engine = GameEngine()
        base_coins = metadata.rewards.get("coins", 100) if metadata.rewards else 100
        engine.load_level(width, height, arrows, base_coins=base_coins)
        
        return engine, metadata

    @staticmethod
    def load_from_file(filepath: str) -> Tuple[GameEngine, LevelMetadata]:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return LevelParser.load_from_json(data)
