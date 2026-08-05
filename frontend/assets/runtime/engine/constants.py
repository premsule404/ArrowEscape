from enum import Enum
from typing import Dict

class GameState(Enum):
    READY = "ready"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

STAR_THRESHOLDS: Dict[str, float] = {
    "three_star": 0.50,
    "two_star": 0.70,
    "one_star": 0.80
}

def calculate_allowed_level_time(total_arrows: int) -> float:
    """
    Centralized function for allowed level time:
    total_allowed_time_seconds = total_number_of_arrows (1 arrow = 1 second).
    """
    return float(total_arrows)

def calculate_stars(elapsed_time: float, total_time: float) -> int:
    """
    Exclusively time-based star calculation formula:
    time_ratio = elapsed_time / total_time
    <= 0.50 -> 3 Stars
    > 0.50 and <= 0.70 -> 2 Stars
    > 0.70 and <= 0.80 -> 1 Star
    > 0.80 -> 0 Stars
    """
    if total_time <= 0:
        return 0
    ratio = elapsed_time / total_time
    if ratio <= STAR_THRESHOLDS["three_star"]:
        return 3
    elif ratio <= STAR_THRESHOLDS["two_star"]:
        return 2
    elif ratio <= STAR_THRESHOLDS["one_star"]:
        return 1
    else:
        return 0

def calculate_coin_reward(stars: int, base_coins: int) -> int:
    """
    Star-based coin reward formula:
    3 Stars -> 100% of base_coins
    2 Stars -> 70% of base_coins
    1 Star  -> 50% of base_coins
    0 Stars -> 0 coins
    """
    if stars == 3:
        return base_coins
    elif stars == 2:
        return round(base_coins * 0.70)
    elif stars == 1:
        return round(base_coins * 0.50)
    else:
        return 0
