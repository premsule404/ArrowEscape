from typing import Optional, List, Tuple
import copy
from .models import Arrow, Position, Direction
from .board import Board
from .events import EventDispatcher

class GameEngine:
    def __init__(self):
        self.board: Optional[Board] = None
        self.events = EventDispatcher()
        self.move_history: List[Tuple[str, Position]] = [] # stores (arrow_id, original_pos)
        self.initial_state: Optional[Board] = None

    def load_level(self, width: int, height: int, arrows: List[Arrow]):
        self.board = Board(width, height)
        for arrow in arrows:
            self.board.add_arrow(arrow)
        self.initial_state = self.board.clone()
        self.move_history.clear()

    def can_move(self, arrow: Arrow) -> bool:
        """Checks if the arrow has a clear path to the edge of the board."""
        if not self.board:
            return False
            
        dx, dy = arrow.direction.value
        current_x, current_y = arrow.position.x, arrow.position.y

        while True:
            current_x += dx
            current_y += dy
            pos = Position(current_x, current_y)
            
            if not self.board.is_in_bounds(pos):
                # Reached the edge successfully
                return True
            
            if self.board.get_arrow_at(pos) is not None:
                # Path is blocked
                return False

    def tap_arrow(self, arrow_id: str) -> bool:
        if not self.board or arrow_id not in self.board.arrows:
            return False
            
        arrow = self.board.arrows[arrow_id]
        
        if self.can_move(arrow):
            self.events.dispatch("on_arrow_slide", arrow)
            self.move_history.append((arrow.id, arrow.position))
            self.board.remove_arrow(arrow.id)
            
            if self.is_level_complete():
                self.events.dispatch("on_win")
            return True
        else:
            self.events.dispatch("on_arrow_blocked", arrow)
            return False

    def undo(self) -> bool:
        if not self.move_history or not self.board or not self.initial_state:
            return False
            
        arrow_id, original_pos = self.move_history.pop()
        
        original_arrow = self.initial_state.arrows[arrow_id]
        restored_arrow = copy.deepcopy(original_arrow)
        self.board.add_arrow(restored_arrow)
        
        self.events.dispatch("on_undo", restored_arrow)
        return True

    def restart(self):
        if self.initial_state:
            self.board = self.initial_state.clone()
            self.move_history.clear()
            self.events.dispatch("on_restart")

    def is_level_complete(self) -> bool:
        return self.board is not None and len(self.board.arrows) == 0
