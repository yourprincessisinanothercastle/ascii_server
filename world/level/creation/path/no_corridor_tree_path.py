import random
from typing import Type, List, Tuple
from world.level.tile import TILE_NAMES
from world.level.creation import LevelBudget, GeneratorOutput
from world.level.creation.area import SquareRoom, AreaBudget, AreaGenerator

from world.level.creation.entity import EntityBudget
from world.level.creation.path import PathGenerator

import logging
logger = logging.getLogger(__name__)


class NoCorridorTreePath(PathGenerator):
    """
    This generator creates square rooms packed without corridors.
    """
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        self.level_budget = level_budget
        return self._walk_path()

    # TODO remove test function
    def fake_gen(self, tp=160):
        l = LevelBudget(monster_pool=[], entity_points=200, tile_points=tp, area_pool=[SquareRoom], area_weight=[1])
        return self.generate(l)

    def _get_area_monster_pool(self):
        return self.level_budget.monster_pool

    def _get_layout_directions(self, empty_map: List[List[str]], direction: int,
                               wall_padding: int = 50) -> Tuple[Tuple[int, int], Tuple[int, int], List[int]]:
        """
        Generate starting and ending coordinates (as tuple[0] and tuple[1] resp.)
        It will also return a 3rd tuple containing sideways directions
        Start->end direction = 0, 1, 2, 3 -> up, right, down, left
        """
        width, height = len(empty_map), len(empty_map[0])
        p = wall_padding
        if bool(direction % 2):
            sideways_directions = [0, 2]
            if direction == 1:
                sx, sy, ex, ey = p, round(height / 2), width - p, random.choice(range(0, height))  # left -> right
            else:
                sx, sy, ex, ey = width - p, round(height / 2), p, random.choice(range(0, height))  # right -> left
        else:
            sideways_directions = [1, 3]
            if direction == 0:
                sx, sy, ex, ey = round(width / 2), height - p, random.choice(range(0, width)), p  # bottom -> top
            else:
                sx, sy, ex, ey = round(width / 2), p, random.choice(range(0, width)), height - p  # top -> bottom
        return (sx, sy), (ex, ey), sideways_directions

    def _get_path_areas(self, area_points_list: List[int], min_area_path: int) -> List[List[int]]:
        area_count = len(area_points_list)
        if area_count < min_area_path * 2:
            return [area_points_list]
        else:
            first = random.choice(range(min_area_path, area_count - min_area_path)) + 2  # taking 2 extra for start/end
            return [area_points_list[0:first], area_points_list[first:area_count]]

    def _merge_area(self, area_output: GeneratorOutput, pos: Tuple[int, int]):
        # TODO also merge entities and whatever else is needed
        for idx, col in enumerate(area_output["tiles"]):
            for idy, tile in enumerate(col):
                self.level_map[pos[0] + idx][pos[1] + idy] = tile

    def _walk_path(self):
        # --- area_generators init
        area_points_list = self._get_area_points()
        entity_points_list = self._get_entity_points(area_points_list)
        self.level_map = self._get_empty_map(sum(area_points_list))
        area_generators: List[Type[AreaGenerator]] = self._get_area_generators(len(area_points_list))

        def change_tile(coords, new_name="floor"):
            self.level_map[coords[0]][coords[1]] = TILE_NAMES[new_name]

        # --- setup map layout directions
        map_dir = random.choice([0, 1, 2, 3])  # up, right, down, left
        start, end, sideways_directions = self._get_layout_directions(self.level_map, map_dir)
        sideways_directions.sort(reverse=bool(random.getrandbits(1)))  # randomizes which direction first path takes

        # --- decide which areas goes in which path
        min_area_path = 4
        paths = self._get_path_areas(area_points_list, min_area_path)
        len_main_path = random.choice(range(min_area_path, min(map(len, paths)) - min_area_path))  # rest are side-areas

        # --- generate path by path
        # area_blocks - generated area outputs and info to join them (top-left offset, entry-direction, prev-area index)
        area_history: List[Tuple[Tuple[int, int], int, int, Type[GeneratorOutput]]] = []
        area_cntr, i_start_area, i_end_area = 0, None, None  # indexes to "areas" above
        can_take_mid = False
        for idx, path_area_points_list in enumerate(paths):
            outward_dir = sideways_directions[idx % 2]
            inward_dir = sideways_directions[(idx + 1) % 2]
            has_gone_outward, has_gone_inward = False, False
            side_areas_left = len(path_area_points_list) - len_main_path
            pos = start

            # --- sometimes a path will start off NOT going outwards directly, and map_dir = middle
            if can_take_mid and bool(random.getrandbits(1)):
                can_take_mid = False
                current_dir = map_dir
            else:
                has_gone_outward = True
                current_dir = outward_dir

            # --- generate path areas
            for idy, points in enumerate(path_area_points_list):
                end_offset_x = pos[0] - end[0]  # negative is on left from current pos
                end_offset_y = pos[1] - end[1]  # or above current pos

                area_budget = AreaBudget(tile_points=area_points_list[area_cntr],
                                         doorways=[])  # we don't ask to gen doors, as we will open them up here/outside
                entity_budget = EntityBudget(entity_points=entity_points_list[area_cntr],
                                             monster_pool=self._get_area_monster_pool(),
                                             has_exit=False)
                area_output = area_generators[area_cntr]().generate(entity_budget=entity_budget,
                                                                    area_budget=area_budget,
                                                                    player_spawn_area_count=int(bool(area_cntr == 0)))
                # --- set new pos depending on previous (except for start area)
                # "flip" - aligning rooms in a 2-path scenario, to avoid overlap on "middle" I hang them "outwards"
                # which can otherwise be a problem if the new room is wider/taller than the previous one
                area_w, area_h, pad = len(area_output[0]), len(area_output[0][0]), 1
                flip_alignment = (idx % 2)
                if not area_cntr == 0:
                    x_offset, y_offset = None, None
                    if flip_alignment:
                        prev_area = area_history[area_cntr - 1][3]
                        prev_area_w, prev_area_h = len(prev_area[0]), len(prev_area[0][0])
                        # TODO set the path-2 alignment offsets
                        if map_dir == 0:
                            x_offset = None
                            y_offset = None
                        elif map_dir == 1:
                            x_offset = None
                            y_offset = None
                        elif map_dir == 2:
                            x_offset = None
                            y_offset = None
                        elif map_dir == 3:
                            x_offset = None
                            y_offset = None
                    else:  # 0, 1, 2, 3 - up, right, down, left
                        if map_dir == 0:
                            x_offset = 0
                            y_offset = -(area_h + pad)
                        elif map_dir == 1:
                            x_offset = area_w + pad
                            y_offset = 0
                        elif map_dir == 2:
                            x_offset = 0
                            y_offset = area_h + pad
                        elif map_dir == 3:
                            x_offset = -(area_w + pad)
                            y_offset = 0

                    pos = x_offset, y_offset

                # --- merge and add to history
                self._merge_area(area_output, pos)
                area_history.append((pos, current_dir, area_cntr, area_output))

                # --- control path turning direction
                if area_cntr == 0:
                    i_start_area = area_cntr
                elif not area_cntr == len_main_path:
                    # avoiding direction manipulation for first/last room (shared starting-room for paths)
                    if current_dir is not map_dir:
                        current_dir = map_dir  # after turning, we have to move one step up first before turning again
                    elif random.random() < (idy + 1) / len(path_area_points_list) / 2:
                        if not has_gone_outward:  # before 50% we will turn outwards
                            has_gone_outward = True
                            current_dir = outward_dir
                        elif not has_gone_inward:  # after 50% and before 100% we will turn inwards
                            has_gone_inward = True
                            current_dir = outward_dir
                else:
                    i_end_area = area_cntr
                area_cntr += 1
