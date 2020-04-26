import logging
import uuid
from typing import TYPE_CHECKING, Tuple, List

from world.entity import Entity, ENTITY_TYPE

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from world.level.level import Level


class Creature(Entity):
    '''
    something that could move every tick
    '''

    DIRECTIONS = dict(
        up='up',
        down='down',
        left='left',
        right='right',
    )

    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    ACTION_TIME = dict(
        move=.10,
        hit=.20
    )

    def __init__(self, x, y):
        super().__init__(x, y, ENTITY_TYPE.creature)
        self.room: Level = None
        self.x = 0
        self.y = 0

        self.action_queue: List[Tuple] = []

        self.current_action: Tuple = ()  # ( method, (args,) )
        self.current_action_time: int = 0
        self.uid = uuid.uuid4()
        self.update_sent = False
        self.last_seen_at = None  # (0, 0)

    def is_visible(self):
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:
                    target_tile = self.room.map.get_tile(self.y + row_idx, self.x + col_idx)
                    if target_tile.is_visible:
                        self.last_seen_at = (self.x, self.y)
                        return True
        return False

    @property
    def current_tile(self):
        return self.room.map.tiles[self.y][self.x]

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

    def get_client_info(self):
        is_visible = self.is_visible()
        if is_visible:
            logger.info('visible')
            coords = (self.x, self.y)
        elif self.last_seen_at:
            logger.info('last seen')
            coords = self.last_seen_at
        else:
            logger.info('not seen')
            return False

        return {
            'type': self.type,
            'coords': coords,
            'is_visible': is_visible,
            'color': self.color
        }



    def process_action_queue(self, time_delta: float):
        """
        progress current action further, or poll for new action
        """

        if self.current_action:
            # get action time from dict
            action_time = self.ACTION_TIME[self.current_action[0].__name__]

            # add time delta to current_action_time
            self.current_action_time += time_delta
            logger.debug('current action time: %s' % self.current_action_time)

            if self.current_action_time >= action_time:
                # unpack current_action
                action, (args, kwargs) = self.current_action

                # execute
                action(*args, **kwargs)

                if self.action_queue:
                    # get the next action
                    self.current_action = self.action_queue.pop(0)

                    # set current_action_time to whats left of the last time slot
                    self.current_action_time = self.current_action_time % action_time
                else:
                    self.current_action = None

        else:
            if self.action_queue:
                self.current_action = self.action_queue.pop(0)
                self.current_action_time = 0

    def add_action(self, method, *args, **kwargs):
        action = (method, (args, kwargs))
        logger.debug(action)
        self.action_queue.append(action)
        self.action_queue = self.action_queue[:3]

    def set_coords(self, x, y):
        self.x = x
        self.y = y
