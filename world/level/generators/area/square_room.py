'''
This one generates a standard square kind of room-shape area, with potential irregularities.
'''
from world.level.generators.area._area_generator import AreaGenerator
from world.level.generators.area import AREA_GENERATOR_RESULT

import logging
logger = logging.getLogger(__name__)

W = 'wall'
F = 'floor'
_ = None


class SquareRoom(AreaGenerator):
    def __init__(self):
        super().__init__()
        self.tiles = self.generate()

    def generate(self) -> dict:
        self._player_spawn_areas = [
            [(1, 1), (2, 2)]  # upper left
        ]
        self._monster_spawn_areas = [
            [(5, 7), (6, 8)]  # bottom right
        ]
        return AREA_GENERATOR_RESULT([], [
                [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
            ])
