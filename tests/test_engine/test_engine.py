
from shared.engine.models import Arrow, Position, Direction
from shared.engine.engine import GameEngine

def test_arrow_slide_success():
    engine = GameEngine()
    arrow1 = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow1])
    
    assert engine.can_move(arrow1) is True
    assert engine.tap_arrow("1") is True
    assert engine.is_level_complete() is True

def test_arrow_blocked():
    engine = GameEngine()
    arrow1 = Arrow("1", Position(0, 0), Direction.RIGHT)
    arrow2 = Arrow("2", Position(1, 0), Direction.UP)
    engine.load_level(3, 3, [arrow1, arrow2])
    
    # arrow1 is blocked by arrow2
    assert engine.can_move(arrow1) is False
    assert engine.tap_arrow("1") is False
    
    # arrow2 is free to move UP
    assert engine.can_move(arrow2) is True
    assert engine.tap_arrow("2") is True
    
    # now arrow1 is free
    assert engine.can_move(arrow1) is True
    assert engine.tap_arrow("1") is True
    
    assert engine.is_level_complete() is True

def test_undo():
    engine = GameEngine()
    arrow1 = Arrow("1", Position(0, 0), Direction.RIGHT)
    engine.load_level(3, 3, [arrow1])
    
    engine.tap_arrow("1")
    assert engine.is_level_complete() is True
    
    engine.undo()
    assert engine.is_level_complete() is False
    assert len(engine.board.arrows) == 1
