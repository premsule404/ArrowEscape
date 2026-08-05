from enum import Enum
from dataclasses import dataclass
from typing import NamedTuple

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Position(NamedTuple):
    x: int
    y: int

@dataclass
class Arrow:
    id: str
    position: Position
    direction: Direction
    color_theme: str = "default"
    is_black_master: bool = False
    is_golden_master: bool = False
