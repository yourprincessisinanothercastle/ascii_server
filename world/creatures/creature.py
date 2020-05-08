import logging
import uuid
from typing import TYPE_CHECKING, Tuple, List

from util.coord_helpers import distance
from util.field_of_view import fov
from world.entity import Entity, ENTITY_TYPE

if TYPE_CHECKING:
    from world.creatures import Player

logger = logging.getLogger(__name__)


class Creature(Entity):
    """
    something that could move every tick
    """
    DIRECTIONS = dict(
        up='up',
        down='down',
        left='left',
        right='right',
    )

    ACTION_TIME = dict(
        move=.10,
        hit=.20
    )

    creature_type: str  # should be set in each sub-class

    def __init__(self, x: int, y: int,
                 view_radius: int = 0,
                 color: int = 200,
                 life: int = 1,
                 damage: int = 0):
        super().__init__(x, y, ENTITY_TYPE.creature)

        self.action_queue: List[Tuple] = []

        self.current_action: Tuple = ()  # ( method, (args,) )
        self.current_action_time: int = 0
        self.uid = uuid.uuid4()
        self.update_sent = False
        self.last_seen_at = None  # (0, 0)
        
        self.direction = Creature.DIRECTIONS['right']

        self.view_radius = view_radius
        self.update_sent = False
        self.color = color

        self._visible_tile_coords = []  # temporary list to check if players are visible

        self.life = life
        self.damage = damage

    def is_visible(self):
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:
                    target_tile = self.floor.map.get_tile(self.y + row_idx, self.x + col_idx)
                    if target_tile.is_visible:
                        self.last_seen_at = (self.x, self.y)
                        return True
        return False

    @property
    def current_tile(self):
        return self.floor.map.tiles[self.y][self.x]

    def collides_with_coords(self, x, y):
        """
        test own hitbox against collision on x, y
        
        :param x: 
        :param y: 
        :return: 
        """
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:
                    hitbox_tile_coords = self.x + col_idx, self.y + row_idx
                    if hitbox_tile_coords == (x, y):
                        return True
        return False

    def collides_with_entity(self, entity):
        """
        test own hitbox agains another entities hitbox
        
        :param entity: 
        :return: 
        """
        for row_idx, row in enumerate(entity.HITBOX):
            for col_idx, col in enumerate(row):
                if col:
                    hitbox_tile_coords = entity.x + col_idx, entity.y + row_idx
                    collides = self.collides_with_coords(*hitbox_tile_coords)
                    if collides:
                        return True
        return False

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

    def get_client_info(self):
        is_visible = self.is_visible()
        if is_visible:
            coords = (self.x, self.y)
        elif self.last_seen_at:
            coords = self.last_seen_at
        else:
            return False

        return {
            'type': self.creature_type,
            'coords': coords,
            'is_visible': is_visible,
            'color': self.color,
            'sprite_state': self.get_sprite_state(),
            'direction': self.direction
        }

    def get_sprite_state(self):
        if self.current_action:
            return self.current_action[0].__name__
        return 'idle'

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
                    self.current_action = self.action_queue.pop(0)

                    # set current_action_time to whats left of the last time slot
                    self.current_action_time = self.current_action_time % action_time
                else:
                    self.current_action = None

        else:
            if self.action_queue:
                self.current_action = self.action_queue.pop(0)
                self.current_action_time = 0

    def add_action(self, method, *args, flush=False, **kwargs):
        action = (method, (args, kwargs))
        if flush:
            self.action_queue = []
        self.action_queue.append(action)
        self.action_queue = self.action_queue[:3]

    # ---------------------------------------------------------- creature default behavior

    def _visit(self, x, y):
        '''
        called for every visible tile
        needs to return true if tile blocks sight
        '''

        self._visible_tile_coords.append((x, y))
        if y > len(self.floor.map.tiles) - 1 or y < 0:
            return True
        if x > len(self.floor.map.tiles[y]) - 1 or x < 0:
            return True
        return self.floor.map.tiles[y][x].block_sight

    def get_closest_player(self):
        closest_player = None
        closest_player_distance = None

        # update visible tile coords
        self._visible_tile_coords = []
        fov(self.x, self.y, self.view_radius, self._visit)

        # get players on visible tiles
        for player in self.floor.players:
            if (player.x, player.y) in self._visible_tile_coords:
                distance_player = distance(self.x, self.y, player.x, player.y)
                if not closest_player_distance or \
                        closest_player_distance > distance_player:
                    closest_player = player
                    closest_player_distance = distance_player
        return closest_player

    # TODO function to handle being hit (and dying if self.life < 1)

    def attack(self):
        for player in self.floor.players:
            if self.collides_with_entity(player):
                player.hit_points -= self.damage
                player.update_sent = False
        self.add_action(self.cooldown)

    def cooldown(self):
        """
        do nothing for a while after an attack

        :return:
        """
        pass

    def update(self):
        if not self.action_queue:
            closest_player: Player = self.get_closest_player()
            if closest_player:
                logger.info('closest player: %s, %s' % (closest_player.x, closest_player.y))
                logger.info('self: %s, %s' % (self.x, self.y))
                if self.collides_with_entity(closest_player):
                    logger.info('hit!')
                    self.add_action(self.hit)

                else:
                    if closest_player.x < self.x:
                        dx = -1
                    elif closest_player.x > self.x:
                        dx = 1
                    else:
                        dx = 0

                    if closest_player.y < self.y:
                        dy = -1
                    elif closest_player.y > self.y:
                        dy = 1
                    else:
                        dy = 0

                    self.add_action(self.move, dx, dy, flush=True)