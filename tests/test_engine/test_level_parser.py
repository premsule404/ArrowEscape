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
    
def test_invalid_bounds():
    json_data = {
      "grid": { "width": 2, "height": 2 },
      "arrows": [
        { "id": "a1", "x": 3, "y": 3, "direction": "UP" }
      ]
    }
    try:
        LevelParser.load_from_json(json_data)
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True
