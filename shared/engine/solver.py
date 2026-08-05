from typing import List, Optional
from .board import Board
from .engine import GameEngine

class HintSystem:
    def __init__(self, engine: GameEngine):
        self.engine = engine

    def get_next_hint(self) -> Optional[str]:
        """
        Uses DFS to find a valid sequence of arrow IDs that solves the puzzle.
        Returns the ID of the first arrow to tap, or None if unsolvable.
        """
        if not self.engine.board:
            return None
            
        solution = self._solve(self.engine.board)
        if solution:
            return solution[0]
        return None

    def _solve(self, board: Board, visited_states=None) -> Optional[List[str]]:
        if visited_states is None:
            visited_states = set()
            
        if len(board.arrows) == 0:
            return []
            
        state_sig = frozenset(board.arrows.keys())
        if state_sig in visited_states:
            return None
        visited_states.add(state_sig)
        
        temp_engine = GameEngine()
        temp_engine.board = board
        
        movable = [aid for aid, arrow in board.arrows.items() if temp_engine.can_move(arrow)]
        if not movable:
            return None
            
        for arrow_id in movable:
            next_board = board.clone()
            next_board.remove_arrow(arrow_id)
            
            path = self._solve(next_board, visited_states)
            if path is not None:
                return [arrow_id] + path
                
        return None
