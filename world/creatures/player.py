import logging
import random

from world.creatures._creature import Creature
from world.creatures.projectile import Projectile

logger = logging.getLogger(__name__)


class Player(Creature):
    CHARS = dict(
        up='◓',
        down='◒',
        left='◐',
        right='◑',
    )

    ACTION_TIME = dict(
        move=.10,
        hit=.20
    )

    def __init__(self, websocket):
        super().__init__(0, 0)
        self.direction = Creature.DIRECTIONS['left']

        self.fov_needs_update = True
        self.view_radius = 10
        
        self.speed = 1
        self.accuracy = 1
        self.strength = 1
        self.color = random.randint(0, 254)
        
        self.websocket = websocket

    @property
    def char(self):
        return Player.CHARS[self.direction]

    def add_action(self, method, *args, **kwargs):
        action = (method, (args, kwargs))
        logger.debug(action)
        self.action_queue.append(action)
        self.action_queue = self.action_queue[:3]

    def move(self, dx, dy):
        target_tile = self.room.map.tiles[self.y + dy][self.x + dx]
        if dx > 0:
            new_direction = Player.DIRECTIONS['right']
        elif dx < 0:
            new_direction = Player.DIRECTIONS['left']
        elif dy > 0:
            new_direction = Player.DIRECTIONS['down']
        else:
            new_direction = Player.DIRECTIONS['up']

        if self.direction != new_direction:
            self.direction = new_direction
            return

        if not target_tile.blocked:
            self.fov_needs_update = True

            self.x += dx
            self.y += dy
        
    def shoot(self):
        p = Projectile()
        p.shoot(self.direction)
        self.room.spawn_creature(p, self.x, self.y)
        