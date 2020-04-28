from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.level.level import Level

# use one of these for inherited types
ENTITY_TYPE = Enum('ENTITY_TYPE', 'creature item interact exit')


class Entity:
    """
    something in a level that has coords on a map tile
    """
    floor: 'Level'
    x: int
    y: int

    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    def __init__(self, x: int, y: int, entity_type: ENTITY_TYPE):
        self.entity_type: ENTITY_TYPE = entity_type
        self.floor = None
        self.x = x
        self.y = y

    def set_coords(self, x: int, y: int):
        self.x = x
        self.y = y
