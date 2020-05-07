import random
from typing import List, NamedTuple
from world.level.creation import IGenerator
from world.creatures import Bestiary, Creature

import logging
logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Creature]),  # possible subset (less than level subset) of monsters to draw from
    ("entity_points", int),
    ("has_exit", bool)
])


class EntityGenerator(IGenerator):
    """
    With a budget, generates a collection of entities for distribution within an area (only what, not where)
    """
    entity_budget: EntityBudget

    # noinspection PyMethodOverriding
    def generate(self,
                 entity_budget: EntityBudget,
                 tiles: List[List[str]]) -> List[Creature]:
        self._tiles = tiles
        self.entity_budget = entity_budget

        viable = []
        for idx, column in enumerate(self._tiles):
            for idy, tile in enumerate(column):
                if tile == "floor":
                    viable.append((idx, idy))
        # TODO do better than one of each
        creatures = []
        for creature in Bestiary.get_creature_pool():
            coords = viable.pop(random.choice(range(0, len(viable))))
            creatures.append(creature(x=coords[0], y=coords[1]))
        return creatures

    # noinspection PyMethodOverriding
    def draw(self):
        # Could output entities in a more readable fashion than as_json if we want, at some point
        raise NotImplementedError
