from typing import List, NamedTuple
from enum import Enum
from world.level.generators.area.square_room import SquareRoom

generator = {
    'square_room': SquareRoom
}

KEY_ENTITIES = "entities"
KEY_TILES = "tiles"

# starting point, we need to define entity fields further
# specific entity ex: PLAYER = namedtuple('ENTITY', type=ENTITY_TYPE.player ENTITY._fields + ('lookups',)
ENTITY_TYPE = Enum('ENTITY_TYPE', 'player monster item door exit')
ENTITY = NamedTuple("ENTITY", type=ENTITY_TYPE)

AREA_GENERATOR_RESULT = NamedTuple("AREA_GENERATOR_RESULT", [
    (KEY_ENTITIES, List[ENTITY]),  # TODO typehint for entity elements
    (KEY_TILES, List[str])
])
