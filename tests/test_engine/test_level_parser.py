from shared.engine.level_parser import LevelParser

def test_valid_json_parsing():
    json_data = {
      "id": "level001",
      "name": "Test Level",
      "difficulty": 1,
      "grid": { "width": 4, "height": 4 },
      "arrows": [
        { "id": "a1", "x": 1, "y": 1, "direction": "UP", "theme": "default" },
        { "id": "a2", "x": 1, "y": 2, "direction": "RIGHT", "theme": "default" }
      ],
      "rewards": {}
    }
    
    engine, metadata = LevelParser.load_from_json(json_data)
    assert metadata.id == "level001"
    assert metadata.name == "Test Level"
    assert engine.board.width == 4
    assert engine.board.height == 4
    assert len(engine.board.arrows) == 2
    
def test_all_50_production_levels_audit():
    import os, json
    levels_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "assets", "runtime", "levels")
    assert os.path.exists(levels_dir), "Levels directory missing!"

    for i in range(1, 51):
        filename = f"level{i:03d}.json"
        filepath = os.path.join(levels_dir, filename)
        assert os.path.exists(filepath), f"Missing level file: {filename}"

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        engine, metadata = LevelParser.load_from_json(data)
        assert engine.board is not None
        assert len(engine.board.arrows) > 0, f"{filename} has 0 arrows!"
        assert engine.total_time == float(len(engine.board.arrows)), f"{filename} time limit formula mismatch!"
        assert engine.hearts == 3, f"{filename} hearts not set to 3!"
        assert engine.is_game_over == False
