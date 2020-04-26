import logging
import random
from typing import TYPE_CHECKING

from world.creatures.creature import Creature

logger = logging.getLogger(__name__)


class Explosion(Creature):
    def move(self, dx, dy):
        pass

    def __init__(self):
        super().__init__(0, 0)

        self.ACTION_TIME = dict(
            die=1
        )

    def die(self):
        self.room.remove_creature(self)
