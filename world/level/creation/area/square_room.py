import math
from typing import List
from world.level.creation.area import AreaGenerator

import logging
logger = logging.getLogger(__name__)


class SquareRoom(AreaGenerator):

    def _generate_tiles(self) -> List[List[str]]:
        W = 'wall'
        F = 'floor'

        area = []
        tiles = round(math.sqrt(self.area_budget.tile_points))
        for x in range(0, tiles):
            col = []
            area.append(col)
            for y in range(0, tiles):
                col.append(F)
        area[0][0] = "tl"
        return area

