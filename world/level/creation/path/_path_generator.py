import math
import random
from typing import Type, List, Tuple, NamedTuple, Set

from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import AreaGenerator
from world.level.creation import LevelBudget

import logging
logger = logging.getLogger(__name__)

# helper structure for 2d operations in this generator, maybe put it in a "common" package if its useful elsewhere
Rect = NamedTuple("rect", [
    ("xy", Tuple[int, int]),
    ("w", int),
    ("h", int)
])


class PathGenerator(IGenerator):
    """ Creates a level map """
    _EMPTY_TILE = "wall"
    level_budget: LevelBudget

    # noinspection PyMethodOverriding
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        # in the very end, area generators have all been called and we can merge all tiles to a big level
        raise NotImplementedError

    def _get_area_generators(self, area_count: int) -> List[Type[AreaGenerator]]:
        """ Compose a list of area_generators (un-instantiated) to be generated for this level """
        return random.choices(self.level_budget.area_pool,
                              self.level_budget.area_weight,
                              k=area_count)

    def _get_empty_map(self, total_area_budget_points: int, padding_factor: float = 5) -> List[List[str]]:
        """
        While ad-hoc, we base the initial map on squaring and padding the levels tile budget points
        TODO this will cause a lot of empty space - override this default function to slim down the maps

        The idea is that it's up to each path generator to translate area points into a real map, depending on what
        you want the path_generator to create.
        """
        dim = math.ceil(math.sqrt(total_area_budget_points) * padding_factor)
        empty_map = []
        for n1 in range(0, dim):
            col = []
            empty_map.append(col)
            for n2 in range(0, dim):
                col.append(self._EMPTY_TILE)
        return empty_map

    def _trim_excess_tiles(self, tile_names_to_keep: List[str]):
        left, right, top, bottom = None, None, None, None
        for idx, column in enumerate(self._tiles):
            for idy, cell in enumerate(column):
                if cell in tile_names_to_keep:
                    if not left:
                        left = idx
                    right = idx
                    if not top or idy < top:
                        top = idy
                    if not bottom or idy > bottom:
                        bottom = idy
        if left: left += -1  # somehow, these additions cause false values if I do it in the loops above - dont get it
        if right: right += 2
        if top: top += -1
        if bottom: bottom += 2
        self._tiles = self._tiles[left:right]
        for _idy, _column in enumerate(self._tiles):
            self._tiles[_idy] = _column[top:bottom]
        for entity in self._entities:  # have to shift entities as well
            if left:
                entity.x -= left
            if top:
                entity.y -= top

    def _unstack_entities(self):
        """ Path_generators are allowed to overlap areas and thus might stack entities """
        occupied = dict()
        for e in self._entities:
            key = f'x{e.x}y{e.y}'
            if key not in occupied:
                occupied[key] = []
            occupied[key].append(e)

        moves = [-1, 0, 1]

        def get_adjacent_unoccupied_coord(x, y, start_pos):
            if f'x{x}y{y}' not in occupied:
                return x, y
            elif x == start_pos[0] + 1 and y == start_pos[1] + 1:
                return None  # no adjacent tiles left to check
            else:
                xi, yi = moves.index(start_pos[0] - x), moves.index(start_pos[1] - y)
                if len(moves) - 1 == yi:
                    _y = moves[0]
                    _x = moves[xi + 1]  # skipping condition for ending, as "elif" above should block it
                else:
                    _x = moves[1]  # stay the same
                    _y = moves[yi + 1]
                return get_adjacent_unoccupied_coord(x + _x, y + _y, start_pos)

        for key, entities in occupied.items():
            if len(entities) > 1:
                for entity in entities:
                    coords = get_adjacent_unoccupied_coord(entity.x, entity.y, (entity.x, entity.y))
                    if coords:
                        entity.x, entity.y = coords
                    else:
                        self._entities.remove(entity)  # TODO delete when there's no free space (simple for now)

    def _get_entity_points(self, area_points: List[int]):
        # TODO not yet sure what im balancing points against, so simply the same as area for now
        return area_points.copy()

    def _get_area_points(self) -> List[int]:
        """ Divide budget somewhat randomly between a somewhat random amount of areas :-) """
        min_size = 36
        max_size = min(round(self.level_budget.tile_points / 2), 200)  # TODO very rough placeholder
        min_areas, max_areas = 3, 25

        rest = round(self.level_budget.tile_points * 2)
        areas = []

        def get_size():
            # TODO might want a weighed distribution - should big rooms be as common as medium?
            return random.randrange(min_size, max_size)

        while rest > 0:
            next_area = get_size()

            if next_area > rest > min_size:
                areas.append(rest)
                rest = 0
            elif rest <= min_size:
                rest = 0
            else:
                areas.append(next_area)
                rest -= next_area

        while len(areas) < min_areas:
            areas.append(get_size())

        if len(areas) > max_areas:
            areas = areas[0:max_areas]

        areas.reverse()  # there's a slightly larger chance for a small room at the end, which is nicer for player start
        #print("AREAS", len(areas), areas)
        return areas

    def _merge_area(self, area_output: GeneratorOutput, pos: Tuple[int, int]):
        entities_lookup = dict()
        for e in area_output.entities:
            key = f'x{e.x}y{e.y}'
            if key not in entities_lookup:
                entities_lookup[key] = []
            entities_lookup[key].append(e)

        for idx, col in enumerate(area_output.tiles):
            for idy, tile in enumerate(col):
                self._tiles[pos[0] + idx][pos[1] + idy] = tile
                e_key = f'x{idx}y{idy}'
                if e_key in entities_lookup:
                    entities = entities_lookup[e_key]
                    for entity in entities:
                        entity.x = pos[0] + idx
                        entity.y = pos[1] + idy
                        self._entities.append(entity)

    def _connect_areas(self, prev_area_rect: Rect, area_rect: Rect,
                       new_tile_name: str, mutable_tile_names: List[str],
                       must_connect=True) -> Tuple[int, int] or None:
        """
        Will open a path between 2 areas by running a straight line as long as "mutable_tile_names"
        are encountered along the way. The path will stop if a non-mutable tile is found and considered done.
        Assumes that tiles represented by both area Rects are found in self._tiles.

        Returns connection starting coords ("None" if no connection was made)
        """
        area_intersections = self._get_rect_intersections(prev_area_rect, [area_rect],
                                                          exclude_single_axis_overlap=False)
        if not area_intersections:
            if must_connect:
                raise IndexError("Neighbouring areas were not generated with overlapping X or Y-axis")
            else:
                return None

        def recursive_bulldoze(_x, _y, step_offset: Tuple[int, int]):
            if self._tiles[_x][_y] in mutable_tile_names:
                self._tiles[_x][_y] = new_tile_name
                new_x, new_y = _x + step_offset[0], _y + step_offset[1]
                if new_x < len(self._tiles) and new_y < len(self._tiles[0]):
                    recursive_bulldoze(new_x, new_y, step_offset)

        len_limit = 20  # Upper limit for how long the connection corridor can run
        if prev_area_rect.xy[0] > area_rect.xy[0]:
            distance_x = area_rect.xy[0] + area_rect.w - prev_area_rect.xy[0]
        else:
            distance_x = prev_area_rect.xy[0] + prev_area_rect.w - area_rect.xy[0]

        if prev_area_rect.xy[1] > area_rect.xy[1]:
            distance_y = area_rect.xy[1] + area_rect.h - prev_area_rect.xy[1]
        else:
            distance_y = prev_area_rect.xy[1] + prev_area_rect.h - area_rect.xy[1]

        x, y = None, None
        if area_intersections[0][0] and abs(distance_y) < len_limit:
            # areas will connect along y-axis (as x-axis intersection is not empty)
            x = random.choice(list(area_intersections[0][0]))
            y = prev_area_rect.xy[1] if prev_area_rect.xy[1] > area_rect.xy[1] else area_rect.xy[1]
            # making sure that both sides of the new xy is opened up (in case a Rect has walls within it)
            recursive_bulldoze(x, y - 1, (0, -1))
            recursive_bulldoze(x, y + 1, (0, 1))
            self._tiles[x][y] = new_tile_name  # always fill the inner-edge, since we step away from it
        elif area_intersections[0][1] and abs(distance_x) < len_limit:
            x = prev_area_rect.xy[0] if prev_area_rect.xy[0] > area_rect.xy[0] else area_rect.xy[0]
            y = random.choice(list(area_intersections[0][1]))
            recursive_bulldoze(x - 1, y, (-1, 0))
            recursive_bulldoze(x + 1, y, (1, 0))
            self._tiles[x][y] = new_tile_name
        return x, y if x and y else None

    def _get_rect_intersections(self, rect: Rect, other_area_rects: List[Rect],
                                exclude_single_axis_overlap: bool = True) -> List[Tuple[Set[int], Set[int]]]:
        """
        Check for overlap between rectangles (Rect)
        """
        intersections = []
        rx = range(rect.xy[0], rect.xy[0] + rect.w)
        ry = range(rect.xy[1], rect.xy[1] + rect.h)
        for other in other_area_rects:
            ox = range(other.xy[0], other.xy[0] + other.w)
            oy = range(other.xy[1], other.xy[1] + other.h)
            isx = set(rx).intersection(ox)
            isy = set(ry).intersection(oy)
            if exclude_single_axis_overlap:
                if bool(isx) and bool(isy):  # both axis need to have intersections to be a 2d overlap
                    intersections.append((isx, isy))
            else:
                if bool(isx) or bool(isy):
                    intersections.append((isx, isy))
        return intersections