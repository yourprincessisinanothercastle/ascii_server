import random
from typing import List, NamedTuple, Tuple

from world.creatures.bestiary import Appearance
from world.entity import InteractionRules
from world.interactables import LevelExit
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.invalid_output import InvalidOutputException

import logging
logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Appearance]),  # possible subset (less than level subset) of monsters to draw from
    ("entity_points", int),
    ("level_connect_number", int)  # the level-number the exit should lead to | -1 indicates no exit
])


class EntityGenerator(IGenerator):
    """
    With a budget, generates a collection of entities for distribution within an area (only what, not where)
    """
    _EMPTY_TILES: List[str] = ["floor"]
    _viable_coords: List[Tuple[int, int]] = []  # make sure you pop() from this list to avoid local stacking

    entity_budget: EntityBudget

    # noinspection PyMethodOverriding
    def generate(self,
                 entity_budget: EntityBudget,
                 tiles: List[List[str]]) -> GeneratorOutput:
        self._tiles = tiles
        self.entity_budget = entity_budget

        for idx, column in enumerate(self._tiles):
            for idy, tile in enumerate(column):
                if tile in self._EMPTY_TILES:
                    self._viable_coords.append((idx, idy))

        self._add_exit()
        self._add_creatures()

        # we do not include self._tiles in GeneratorOutput as default, they're just for checking
        # if we want entities to make changes, make a sub-class to alter layout for specific conditions tied to an area
        return GeneratorOutput(entities=self._entities, tiles=[])

    def _generate_creature(self):
        pass

    def _add_exit(self, minimum_spawn_area=4):
        if self.entity_budget.level_connect_number != -1:
            has_exit = False
            reserved_tiles = []
            for idx, pos in enumerate(self._viable_coords):
                reserved_tiles = []
                adjacent = self.get_adjacent(pos[0], pos[1])
                free_cnt = 0
                for neighbour in adjacent:
                    if neighbour[0] in self._EMPTY_TILES:
                        free_cnt += 1
                        reserved_tiles.append(idx)
                if len(reserved_tiles) >= minimum_spawn_area:
                    # disables exits that go up from start-level
                    rules = InteractionRules(trigger_use=(self.entity_budget.level_connect_number > 0))
                    self._entities.append(LevelExit(pos[0], pos[1],
                                                    self.entity_budget.level_connect_number,
                                                    interaction_rules=rules))
                    has_exit = True
                    break
            if has_exit:
                for index in reserved_tiles:
                    self._viable_coords.pop(index)  # remove spawn areas so we don't generate other stuff there
            else:
                raise InvalidOutputException("Could not fit an exit with adjacent free tiles in area")

    def _add_creatures(self):
        rest = self.entity_budget.entity_points
        while rest > 0:
            affordable = list(filter(lambda a: a.price <= rest, self.entity_budget.monster_pool))
            if len(affordable) == 0 or len(self._viable_coords) == 0:
                return  # out of points or available space

            weights = list(map(lambda a: a.weight, affordable))
            appearance = random.choices(affordable, weights, k=1)[0]
            rest -= appearance.price

            # TODO simple random place right now, no clustering for real monster packs YET
            coords = self._viable_coords.pop(random.choice(range(0, len(self._viable_coords))))
            self._entities.append(appearance.creature_class(x=coords[0], y=coords[1]))

    # noinspection PyMethodOverriding
    def draw(self):
        # Could output entities in a more readable fashion than as_json if we want, at some point
        raise NotImplementedError
