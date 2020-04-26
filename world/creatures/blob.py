import logging
import random
import uuid

from util.field_of_view import fov
from world.creatures.creature import Creature
from world.creatures.projectile import Projectile

logger = logging.getLogger(__name__)


class Blob(Creature):
    type = 'blob'

    def __init__(self):
        super().__init__(0, 0)
        self.direction = Creature.DIRECTIONS['left']

        self.view_radius = 0
        self.update_sent = False
        self.color = 200

    def update(self, actions):
        for action in actions:
            if action == 'up':
                self.add_action(self.move, 0, -1)
            elif action == 'down':
                self.add_action(self.move, 0, 1)
            elif action == 'left':
                self.add_action(self.move, -1, 0)
            elif action == 'right':
                self.add_action(self.move, 1, 0)
            else:
                logger.warning('unknown action %s' % action)
