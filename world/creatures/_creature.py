import logging
from typing import TYPE_CHECKING, Tuple, List

from world.thing import Thing

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from world.rooms.room import Room



class Creature(Thing):
    '''
    something that could move every tick
    '''

    DIRECTIONS = dict(
        up='up',
        down='down',
        left='left',
        right='right',
    )

    def __init__(self, x, y):
        super().__init__(x, y)
        self.room: Room = None
        self.x = 0
        self.y = 0

        self.action_queue: List[Tuple] = []

        self.current_action: Tuple = ()  # ( method, (args,) )
        self.current_action_time: int = 0

    @property
    def current_tile(self):
        return self.room.map.tiles[self.y][self.x]

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

    def move(self, dx, dy):
        raise NotImplementedError
