from typing import Callable

from world.interactables.interactable import Interactable, InteractionRules


class LevelExit(Interactable):
    level_number: int  # as in, if we generate level 2, the exits should be created with a number higher or lower.

    HITBOX = [
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    def __init__(self, x: int, y: int, level_number: int,
                 interaction_rules: InteractionRules = None, callback: Callable = None):
        super().__init__(x, y, interaction_rules, callback)
        self.level_number = level_number
        self.sprite_name = 'level_exit'

    def _on_interact(self) -> int:
        return self.level_number
