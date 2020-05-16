import uuid
from enum import Enum
from typing import TYPE_CHECKING, NamedTuple, Tuple, List

if TYPE_CHECKING:
    from world.level.level import Level


class DIRECTION(str, Enum):
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'


# use one of these for subclass types to keep otherwise similar entities apart
class ENTITY_TYPE(str, Enum):
    """
    normal Enums are not json serializable
    this is a workaround for string-enums
    """
    creature = 'creature'
    item = 'item'
    interact = 'interact'


# scheme for if something was able to affect and entity - compared to its allowed interactions
class InteractionRules(NamedTuple):
    trigger_use: bool = False  # all should be False by default
    trigger_hit: bool = False
    trigger_aoe: bool = False
    # add more rules ...


# scheme for parameters that interaction events use (when generic specific parameters are needed)
class InteractionData(NamedTuple):
    originator: 'Entity' = None
    physical_dmg: float = 0
    poison_dmg: float = 0
    fire_dmg: float = 0
    ice_dmg: float = 0
    lightning_dmg: float = 0
    direction: DIRECTION = None
    # whatever other generic data that we might be interested in checking on


class Entity:
    """
    something in a level that has coords on a map tile
    """
    _interaction_rules: InteractionRules
    floor: 'Level'
    x: int
    y: int
    
    color = None

    ACTION_TIME = dict(
        move=.10,
        attack=.20,
        interact=1.00,
    )

    DIRECTIONS = DIRECTION

    HITBOX = [
        [None, None, None],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    sprite_name: str

    def __init__(self, x: int, y: int,
                 entity_type: ENTITY_TYPE,
                 interaction_rules: InteractionRules = InteractionRules()):  # default rules = no interaction
        self.entity_type: ENTITY_TYPE = entity_type
        self.floor = None
        self.x = x
        self.y = y

        self.update_sent = False
        self.client_needs_init = False
        self.last_seen_at = None  # (0, 0)

        self.action_queue: List[Tuple] = []
        self.current_action_time: int = 0
        self.current_action: Tuple = ()  # ( method, (args,) )
        self.direction = Entity.DIRECTIONS['right']

        self.uid = uuid.uuid4()

        self.set_interaction_rules(interaction_rules)

    def set_coords(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self):
        pass

    def is_visible(self):
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                if col:
                    target_tile = self.floor.map.get_tile(self.y + row_idx, self.x + col_idx)
                    if target_tile and target_tile.is_visible:
                        self.last_seen_at = (self.x, self.y)
                        return True
        return False

    @property
    def current_tile(self):
        return self.floor.map.tiles[self.y][self.x]

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

    def get_client_info(self):
        is_visible = self.is_visible()
        if is_visible:
            coords = (self.x, self.y)
        elif self.last_seen_at:
            coords = self.last_seen_at
        else:
            return False

        return {
            'entity_type': self.entity_type,
            'sprite_name': self.sprite_name,
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

    def set_interaction_rules(self, interaction_rules: InteractionRules):
        self._interaction_rules = interaction_rules

    def interact(self, interaction_event: InteractionRules, data: InteractionData = None):
        for row_idx, row in enumerate(self.HITBOX):
            for col_idx, col in enumerate(row):
                point = (self.x + row_idx, self.y + col_idx)
                for entity in self.floor.entities:
                    if point == (entity.x, entity.y):
                        entity.run_interaction(interaction_event, data, self)
                        return  # only trigger once, for first encountered eligible entity

    def run_interaction(self, interaction_event: InteractionRules, data: InteractionData,
                        originator: 'Entity' = None):
        """
        Triggered when something thinks it should interact with this entity.
        Pass interaction rules which tells this entity what happened, to see if its eligible.
        These rules are matched against "triggerable" interactions. If they match, _on_interact logic will fire.
        """
        for event, condition in zip(interaction_event, self._interaction_rules):
            if event and condition:  # as in trigger is listed as True for both sides
                return self._on_interact(interaction_event, data, originator)

    def _on_interact(self, interaction_event: InteractionRules, data: InteractionData, originator: 'Entity'):
        """
        When sub-classing an interactable entity, all effect logic should come from these _on_xxx methods
        Originator is the entity that caused the event, and triggers are the conditions that caused the event to fire
        - triggers is only here so you CAN run more specific conditional checks
        - for example, lets say there is a lever, but the lever wont do its specific event yet, though you can still
        - press it and have whatever lever-animation flip it back and forth
        - the lever should always animate, but you need to design conditional logic to check if some larger event fires
        """
        raise NotImplementedError
