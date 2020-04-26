from enum import Enum
from world.level.level import Level

# use one of these for inherited types
ENTITY_TYPE = Enum('ENTITY_TYPE', 'creature item interact exit')


class Entity:
    """
    something that has coords on a map tile
    """
    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]
    floor: Level

    def __init__(self, x, y, entity_type: ENTITY_TYPE):
        self.entity_type: ENTITY_TYPE = entity_type
        self.x = x
        self.y = y

    def set_coords(self, x, y):
        self.x = x
        self.y = y