import logging
import random

from util.field_of_view import fov
from world.creatures.creature import Creature
from world.creatures.projectile import Projectile

logger = logging.getLogger(__name__)


class Player(Creature):
    type = 'player'

    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    FOV_OFFSET = (1, 1)

    ACTION_TIME = dict(
        move=.10,
        hit=.20
    )

    def __init__(self, websocket):
        super().__init__(0, 0)
        self.direction = Creature.DIRECTIONS['left']

        self.view_radius = 10

        self.websocket = websocket
        self.color = random.randint(0, 255)

    def add_action(self, method, *args, **kwargs):
        action = (method, (args, kwargs))
        logger.debug(action)
        self.action_queue.append(action)
        self.action_queue = self.action_queue[:3]

    def update_fov(self):
        fov(self.x + self.FOV_OFFSET[0], self.y + self.FOV_OFFSET[1], self.view_radius, self.floor.map.update_visible)

    def move(self, dx, dy):
        collision = False
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:  # dont collide on Nones
                    target_tile = self.floor.map.get_tile(self.y + row_idx + dy, self.x + col_idx + dx)
                    if target_tile.blocked:
                        collision = True
                        break

        logger.info('moving to %s %s' % (self.x + dx, self.y + dy))

        if not collision:
            logger.info('setting fov update')
            self.floor.field_of_view_needs_update = True
            self.update_sent = False

            self.x += dx
            self.y += dy

    def shoot(self):
        p = Projectile()
        p.shoot(self.direction)
        self.floor.spawn_creature(p, self.x, self.y)

    def get_client_info(self):
        return {
            'coords': (self.x, self.y),
            'color': self.color
        }

    def get_client_init_data(self):
        return {
            'self': self.get_client_info(),
            'map': self.floor.map.serialize_init_state(),
            'players': {str(player.uid): player.get_client_info() for player in self.floor.players if
                        player is not self},
            'creatures': {str(creature.uid): creature.get_client_info() for creature in self.floor.creatures if
                          creature.get_client_info()}
        }

    def get_client_update_data(self):
        update_package = {}
        map_update = self.floor.map.serialize_update_state()
        if map_update:
            update_package['map'] = map_update

        if not self.update_sent:
            update_package['self'] = self.get_client_info()

        players_update = {str(player.uid): player.get_client_info()
                          for player in self.floor.players
                          if player is not self
                          and player.update_sent is False}
        if players_update:
            update_package['players'] = players_update

        creatures_update = {str(creature.uid): creature.get_client_info() for creature in self.floor.creatures if
                            creature.get_client_info()
                            and creature.update_sent is False}

        if creatures_update:
            update_package['creatures'] = creatures_update

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
