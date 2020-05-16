import logging
from typing import TYPE_CHECKING, Tuple, List

from util.coord_helpers import distance
from util.field_of_view import fov
from world.entity import Entity, ENTITY_TYPE, InteractionRules, InteractionData

if TYPE_CHECKING:
    from world.creatures import Player

logger = logging.getLogger(__name__)


class Creature(Entity):
    """
    something that could move every tick
    """

    def __init__(self, x: int, y: int,
                 view_radius: int = 0,
                 color: int = 200,
                 life: int = 1,
                 damage: int = 0):
        super().__init__(x, y, ENTITY_TYPE.creature)

        self.view_radius = view_radius
        self.update_sent = False
        self.color = color

        self._visible_tile_coords = []  # temporary list to check if players are visible

        self.life = life
        self.damage = damage

        # default interaction - set to some specific per creature class if wanted (or in generator for uniques)
        self.set_interaction_rules(InteractionRules(trigger_hit=True, trigger_aoe=True))

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


    # ---------------------------------------------------------- creature default on_events


    def _on_interact(self, interaction_event: InteractionRules, data: InteractionData, originator: 'Entity'):
        if interaction_event.trigger_hit:
            pass  # TODO add default creature stuff to take dmg, get debuffed, or die depending on data

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
                    self.add_action(self.attack)

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