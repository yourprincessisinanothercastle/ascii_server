import logging
import random
import uuid

from util.field_of_view import fov
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

        self.websocket = websocket
        self.update_sent = False

        self.uid = uuid.uuid4()
        self.color = random.randint(0, 255)

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
        logger.info('moving to %s %s' % (self.x + dx, self.y + dy))

        if not target_tile.blocked:
            logger.info('setting fov update')
            self.fov_needs_update = True
            self.update_sent = False

            self.x += dx
            self.y += dy

    def shoot(self):
        p = Projectile()
        p.shoot(self.direction)
        self.room.spawn_creature(p, self.x, self.y)

    def update_field_of_view(self):
        if self.fov_needs_update:
            logger.debug('updating fov')
            for y_coord, row in self.room.map.tiles.items():
                for x_coord, tile in row.items():
                    tile.is_visible = False
            fov(self.x, self.y, self.view_radius, self.room.map.update_visible)
            self.fov_needs_update = False

    def get_client_info(self):
        return {
            'coords': (self.x, self.y),
            'color': self.color
        }

    def get_client_init_data(self):
        map = self.room.map.serialize_init_state()
        return {
            'self': self.get_client_info(),
            'map': map,
            'players': {str(player.uid): player.get_client_info() for player in self.room.players if player is not self}
        }

    def get_client_update_data(self):
        update_package = {}
        update_package['map'] = self.room.map.serialize_update_state()
        if not self.update_sent:
            update_package['self'] = self.get_client_info()
            self.update_sent = True
        update_package['players'] = {str(player.uid): player.get_client_info() for player in self.room.players if player is not self}
        return update_package

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
