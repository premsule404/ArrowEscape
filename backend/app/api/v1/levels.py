import os
import json
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get('', response_model=List[Dict[str, Any]])
def list_official_levels():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    levels_dir = os.path.join(root_dir, "levels")
    
    levels_list = []
    if os.path.exists(levels_dir):
        for i in range(1, 51):
            filepath = os.path.join(levels_dir, f"level{i:03d}.json")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                levels_list.append({
                    "id": data.get("id", f"level{i:03d}"),
                    "level_num": i,
                    "name": data.get("name", f"Level {i}"),
                    "difficulty": data.get("difficulty", 1),
                    "arrows_count": len(data.get("arrows", [])),
                    "timer_seconds": len(data.get("arrows", [])),
                    "base_coins": data.get("rewards", {}).get("coins", 100)
                })
    return levels_list

@router.get('/{level_num}', response_model=Dict[str, Any])
def get_level_data(level_num: int):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    filepath = os.path.join(root_dir, "levels", f"level{level_num:03d}.json")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Level not found")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
