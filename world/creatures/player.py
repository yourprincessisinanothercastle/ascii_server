import logging
import random

from util.field_of_view import fov
from world.creatures._creature import Creature
from world.creatures.projectile import Projectile

logger = logging.getLogger(__name__)


class Player(Creature):
    type = 'player'

    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    BASE = (1, 2)

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

        self.hit_points = 100

        self.keys_pressed = set()

    def update_fov(self):
        fov(self.x + self.FOV_OFFSET[0], self.y + self.FOV_OFFSET[1], self.view_radius, self.room.map.update_visible)

    def get_next_action(self):
        if 'up' in self.keys_pressed:
            return self.move, 0, -1
        elif 'down' in self.keys_pressed:
            return self.move, 0, 1
        elif 'left' in self.keys_pressed:
            return self.move, -1, 0
        elif 'right' in self.keys_pressed:
            return self.move, 1, 0

    def process_action_queue(self, time_delta: float):
        """
        progress current action further, or poll for new action
        """

        if self.current_action:
            # get action time from dict
            action_time = self.ACTION_TIME[self.current_action[0].__name__]

            # add time delta to current_action_time
            self.current_action_time += time_delta

            if self.current_action_time >= action_time:
                # unpack current_action
                action, (args, kwargs) = self.current_action

                # execute
                action(*args, **kwargs)

                if self.action_queue:
                    # get the next action
                    self.current_action = self.get_next_action()

                    # set current_action_time to whats left of the last time slot
                    self.current_action_time = self.current_action_time % action_time
                else:
                    self.current_action = None

        else:
            if self.action_queue:
                self.current_action = self.get_next_action()
                self.current_action_time = 0

    def move(self, dx, dy):
        collision = False
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:  # dont collide on Nones
                    target_tile = self.room.map.get_tile(self.y + row_idx + dy, self.x + col_idx + dx)
                    if target_tile.blocked:
                        collision = True
                        break

        logger.info('moving to %s %s' % (self.x + dx, self.y + dy))

        if not collision:
            logger.info('setting fov update')
            self.room.field_of_view_needs_update = True
            self.update_sent = False

            self.x += dx
            self.y += dy

    def shoot(self):
        p = Projectile()
        p.shoot(self.direction)
        self.room.spawn_creature(p, self.x, self.y)

    def get_client_info(self):
        return {
            'coords': (self.x, self.y),
            'color': self.color,
            'hit_points': self.hit_points,
            'sprite_state': self.get_sprite_state()
        }

    def get_client_init_data(self):
        return {
            'self': self.get_client_info(),
            'map': self.room.map.serialize_init_state(),
            'players': {str(player.uid): player.get_client_info() for player in self.room.players if
                        player is not self},
            'creatures': {str(creature.uid): creature.get_client_info() for creature in self.room.creatures if
                          creature.get_client_info()},
        }

    def get_client_update_data(self):
        update_package = {}
        map_update = self.room.map.serialize_update_state()
        if map_update:
            update_package['map'] = map_update

        if not self.update_sent:
            update_package['self'] = self.get_client_info()

        players_update = {str(player.uid): player.get_client_info()
                          for player in self.room.players
                          if player is not self
                          and player.update_sent is False}
        if players_update:
            update_package['players'] = players_update

        creatures_update = {str(creature.uid): creature.get_client_info() for creature in self.room.creatures if
                            creature.get_client_info()
                            and creature.update_sent is False}

        if creatures_update:
            update_package['creatures'] = creatures_update

        return update_package

    def update(self, actions):
        for key, state in actions:
            if state == 'release':
                self.keys_pressed.remove(key)
            else:
                self.keys_pressed.add(key)
