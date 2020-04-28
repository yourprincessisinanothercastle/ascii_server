from world.level.creation.area.square_room import AreaGenerator, SquareRoom
from typing import NamedTuple

# Add all area generators here, so the level generator can pick them up
AREA_GENERATORS = NamedTuple("AREA_GENERATORS",
                             square_room=SquareRoom
                             )
