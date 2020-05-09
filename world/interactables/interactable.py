from typing import Callable, NamedTuple

from world.creatures import Creature
from world.entity import Entity, ENTITY_TYPE


class InteractionRules(NamedTuple):
    trigger_interact_key: bool = False  # all should be False by default
    trigger_hit: bool = False
    # add more rules ...


class Interactable(Entity):
    _callback: Callable
    _interaction_rules: InteractionRules

    def __init__(self, x: int, y: int, interaction_rules: InteractionRules = None, callback: Callable = None):
        super().__init__(x, y, ENTITY_TYPE.interact)
        self.set_callback(callback)
        self.set_interact_rules(interaction_rules)

    def set_callback(self, callback: Callable):
        # TODO unsure if we will want this - if the game will call interact() directly on entities we might not
        self._callback = callback

    def set_interact_rules(self, interaction_rules: InteractionRules):
        self._interaction_rules = interaction_rules

    def interact(self, interaction_event: InteractionRules):
        """
        This is what the game should trigger, on whatever condition triggers an interactable.
        Then pass a interaction rules object which tells this entity what happened.
        These rules gets matched against "triggerable" interactions. If it matches, the interactable logic will fire.
        """
        for event, condition in zip(interaction_event, self._interaction_rules):
            if event and condition:  # as in trigger is listed as True for both sides
                return self._callback(self._on_interact())

    def _on_interact(self):
        """ When sub-classing a new interactable, all effect logic should come from here """
        raise NotImplementedError

    def get_client_info(self):
        coords = (self.x, self.y)
        return {
            'entity_type': 'interactable',
            'sprite_name': self.sprite_name,
            'coords': coords,
            'is_visible': True,
            'color': 200,
            'sprite_state': 'idle',
            'direction': Creature.DIRECTIONS['right']
        }