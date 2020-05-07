import random
from typing import List, NamedTuple, Type, Tuple, Callable

from world.level.creation import IGenerator, GeneratorOutput
from world.interactables import LevelExit
from world.creatures import Bestiary, Creature

import logging

from world.level.creation._invalid_output import InvalidOutputException

logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Type[Creature]]),  # possible subset (less than level subset) of monsters to draw from
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
                    self._entities.append(LevelExit(pos[0], pos[1], self.entity_budget.level_connect_number))
                    has_exit = True
                    break
            if has_exit:
                for index in reserved_tiles:
                    self._viable_coords.pop(index)  # remove spawn areas so we don't generate other stuff there
            else:
                raise InvalidOutputException("Could not fit an exit with adjacent free tiles in area")

    def _add_creatures(self):
        # TODO do better than one of each from the pool - we want to have weights and chances
        for creature in Bestiary.get_creature_pool():
            if len(self._viable_coords) == 0:
                return  # no more available space
            coords = self._viable_coords.pop(random.choice(range(0, len(self._viable_coords))))
            self._entities.append(creature(x=coords[0], y=coords[1]))

    # noinspection PyMethodOverriding
    def draw(self):
        # Could output entities in a more readable fashion than as_json if we want, at some point
        raise NotImplementedError
