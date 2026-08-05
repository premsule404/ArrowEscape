from typing import Optional, List, Tuple, Dict, Any
import copy
from .models import Arrow, Position, Direction
from .board import Board
from .events import EventDispatcher
from .constants import GameState, calculate_allowed_level_time, calculate_stars, calculate_coin_reward

class GameEngine:
    def __init__(self):
        self.board: Optional[Board] = None
        self.events = EventDispatcher()
        self.move_history: List[Tuple[str, Position]] = []
        self.initial_state: Optional[Board] = None
        self.max_hearts: int = 3
        self.hearts: int = 3
        self.total_arrows_count: int = 0
        self.total_time: float = 30.0
        self.time_remaining: float = 30.0
        self.elapsed_time: float = 0.0
        self.moves_count: int = 0
        self.state: GameState = GameState.READY
        
        # Reward fields
        self.base_coins: int = 100
        self.stars_earned: int = 0
        self.coins_earned: int = 0
        self.time_ratio: float = 0.0

    @property
    def is_game_over(self) -> bool:
        return self.state in (GameState.COMPLETED, GameState.FAILED)

    @property
    def is_paused(self) -> bool:
        return self.state == GameState.PAUSED

    @property
    def remaining_arrows_count(self) -> int:
        return len(self.board.arrows) if self.board else 0

    @property
    def completed_arrows_count(self) -> int:
        return max(0, self.total_arrows_count - self.remaining_arrows_count)

    def load_level(self, width: int, height: int, arrows: List[Arrow], time_limit: Optional[float] = None, base_coins: int = 100):
        self.board = Board(width, height)
        for arrow in arrows:
            self.board.add_arrow(arrow)
        self.initial_state = self.board.clone()
        self.move_history.clear()
        
        self.max_hearts = 3
        self.hearts = 3
        self.total_arrows_count = len(arrows)
        self.moves_count = 0
        self.base_coins = base_coins
        self.stars_earned = 0
        self.coins_earned = 0
        self.time_ratio = 0.0
        self.elapsed_time = 0.0
        self.state = GameState.READY
        
        # Centralized timer formula: total_arrows + 10 seconds (or explicit time_limit if provided)
        if time_limit is not None and time_limit > 0:
            self.total_time = float(time_limit)
        else:
            self.total_time = calculate_allowed_level_time(len(arrows))
            
        self.time_remaining = self.total_time

    def start_game(self):
        """Explicit start or auto-start on first move/tick."""
        if self.state == GameState.READY:
            self.state = GameState.PLAYING
            self.events.dispatch("on_start")

    def pause(self) -> bool:
        """Pause active gameplay."""
        if self.state in (GameState.PLAYING, GameState.READY):
            self.state = GameState.PAUSED
            self.events.dispatch("on_pause")
            return True
        return False

    def resume(self) -> bool:
        """Resume paused gameplay."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.events.dispatch("on_resume")
            return True
        return False

    def can_move(self, arrow: Arrow) -> bool:
        """Checks if the arrow has a clear path to the edge of the board."""
        if not self.board or self.is_game_over:
            return False
            
        dx, dy = arrow.direction.value
        current_x, current_y = arrow.position.x, arrow.position.y

        while True:
            current_x += dx
            current_y += dy
            pos = Position(current_x, current_y)
            
            if not self.board.is_in_bounds(pos):
                return True
            
            if self.board.get_arrow_at(pos) is not None:
                return False

    def tap_arrow(self, arrow_id: str) -> bool:
        if not self.board or arrow_id not in self.board.arrows:
            return False
            
        if self.state == GameState.READY:
            self.start_game()
            
        if self.state != GameState.PLAYING:
            return False
            
        arrow = self.board.arrows[arrow_id]
        self.moves_count += 1
        
        if self.can_move(arrow):
            self.events.dispatch("on_arrow_slide", arrow)
            self.move_history.append((arrow.id, arrow.position))
            self.board.remove_arrow(arrow.id)
            
            if self.is_level_complete():
                self.state = GameState.COMPLETED
                if self.elapsed_time <= 0.0:
                    self.elapsed_time = 0.1
                self.time_ratio = self.elapsed_time / self.total_time if self.total_time > 0 else 1.0
                self.stars_earned = calculate_stars(self.elapsed_time, self.total_time)
                self.coins_earned = calculate_coin_reward(self.stars_earned, self.base_coins)
                
                completion_info = {
                    "elapsed_time": self.elapsed_time,
                    "total_time": self.total_time,
                    "time_ratio": self.time_ratio,
                    "stars": self.stars_earned,
                    "coins": self.coins_earned,
                    "base_coins": self.base_coins,
                    "moves": self.moves_count
                }
                self.events.dispatch("on_win", completion_info)
            return True
        else:
            self.events.dispatch("on_arrow_blocked", arrow)
            self.hearts -= 1
            self.events.dispatch("on_wrong_move", {"hearts": self.hearts})
            
            if self.hearts <= 0:
                self.hearts = 0
                self.state = GameState.FAILED
                self.events.dispatch("on_game_over", {"reason": "out_of_hearts"})
            return False

    def tick_timer(self, delta_seconds: float):
        """Timer ticks ONLY after game state transitions to PLAYING on 1st move."""
        if self.state != GameState.PLAYING:
            return
            
        self.time_remaining -= delta_seconds
        self.elapsed_time += delta_seconds
        
        if self.time_remaining <= 0:
            self.time_remaining = 0.0
            self.state = GameState.FAILED
            self.events.dispatch("on_game_over", {"reason": "times_up"})

    def undo(self) -> bool:
        if not self.move_history or not self.board or not self.initial_state or self.state == GameState.PAUSED:
            return False
            
        arrow_id, original_pos = self.move_history.pop()
        
        original_arrow = self.initial_state.arrows[arrow_id]
        restored_arrow = copy.deepcopy(original_arrow)
        self.board.add_arrow(restored_arrow)
        
        if self.state in (GameState.COMPLETED, GameState.FAILED):
            self.state = GameState.PLAYING
            
        self.events.dispatch("on_undo", restored_arrow)
        return True

    def restart(self):
        if self.initial_state:
            self.board = self.initial_state.clone()
            self.move_history.clear()
            self.hearts = 3
            self.moves_count = 0
            self.elapsed_time = 0.0
            self.stars_earned = 0
            self.coins_earned = 0
            self.time_ratio = 0.0
            self.time_remaining = self.total_time
            self.state = GameState.READY
            self.events.dispatch("on_restart")

    def is_level_complete(self) -> bool:
        return self.board is not None and len(self.board.arrows) == 0
