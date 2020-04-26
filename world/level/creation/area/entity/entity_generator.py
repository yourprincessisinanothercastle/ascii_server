from typing import List, NamedTuple
from world.entity import Entity
from world.creatures import Creature
from world.level.creation import IGenerator

from world.creatures import BESTIARY

import logging
logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Creature]),  # possible subset (less than level subset) of monsters to draw from
    ("entity_points", int)
])


class EntityGenerator(IGenerator):
    """
    With a budget, generates a collection of entities for distribution within an area (only what, not where)
    """
    # noinspection PyMethodOverriding
    def generate(self,
                 entity_budget: EntityBudget,
                 tiles: List[List[str]],
                 player_spawn_count: int = 0,
                 has_exit: bool = False) -> List[Entity]:

        return [
            BESTIARY.blob(4, 4)
        ]
