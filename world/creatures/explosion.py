import logging
import random
from typing import TYPE_CHECKING

from world.creatures.creature import Creature

logger = logging.getLogger(__name__)


class Explosion(Creature):
    def move(self, dx, dy):
        pass

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)

        self.ACTION_TIME = dict(
            die=1
        )

    def die(self):
        self.floor.remove_entity(self)
