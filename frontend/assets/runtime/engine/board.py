from typing import Dict, Optional, List
from .models import Arrow, Position
import copy

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.arrows: Dict[str, Arrow] = {}
        # grid stores arrow IDs. None means empty.
        self.grid: List[List[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]

    def add_arrow(self, arrow: Arrow) -> bool:
        if not self.is_in_bounds(arrow.position):
            return False
        if self.get_arrow_at(arrow.position) is not None:
            return False
        
        self.arrows[arrow.id] = arrow
        self.grid[arrow.position.y][arrow.position.x] = arrow.id
        return True

    def remove_arrow(self, arrow_id: str) -> bool:
        if arrow_id not in self.arrows:
            return False
        
        arrow = self.arrows[arrow_id]
        self.grid[arrow.position.y][arrow.position.x] = None
        del self.arrows[arrow_id]
        return True

    def get_arrow_at(self, pos: Position) -> Optional[Arrow]:
        if not self.is_in_bounds(pos):
            return None
        arrow_id = self.grid[pos.y][pos.x]
        return self.arrows.get(arrow_id) if arrow_id else None

    def is_in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def clone(self) -> 'Board':
        new_board = Board(self.width, self.height)
        new_board.arrows = copy.deepcopy(self.arrows)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board
