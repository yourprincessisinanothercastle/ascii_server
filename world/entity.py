import uuid
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.level.level import Level

# use one of these for inherited types
class ENTITY_TYPE(str, Enum):
    '''
    normal Enums are not json serializable
    this is a workaround for string-enums
    '''
    creature = 'creature'
    item = 'item'
    interact = 'interact'

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
    
    sprite_name: str

    def __init__(self, x: int, y: int, entity_type: ENTITY_TYPE):
        self.entity_type: ENTITY_TYPE = entity_type
        self.floor = None
        self.x = x
        self.y = y

        self.update_sent = False
        self.last_seen_at = None  # (0, 0)

        self.uid = uuid.uuid4()

    def set_coords(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self):
        pass