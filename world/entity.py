import uuid
from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

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
        self.last_seen_at = None  # (0, 0)

        self.uid = uuid.uuid4()

        self.set_interaction_rules(interaction_rules)

    def set_coords(self, x: int, y: int):
        self.x = x
        self.y = y

    def update(self):
        pass

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
