from world.level.creation.area._area_generator import AreaGenerator
from world.level.creation.area.square_room import SquareRoom

# Add all area generators here, so the level generator can pick them up
AREA_GENERATORS = dict(
    square_room=SquareRoom
)
