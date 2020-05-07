import random
from typing import Type, List, Tuple

from world.level.creation.path._path_generator import Rect
from world.level.creation import LevelBudget, GeneratorOutput
from world.level.creation.area import SquareRoom, AreaBudget, AreaGenerator

from world.level.creation.entity import EntityBudget
from world.level.creation.path import PathGenerator

import logging
logger = logging.getLogger(__name__)


class TwoPaths(PathGenerator):
    """
    This generator creates two paths (when able) which are likely to connect near their ends.
    There's also a moderate chance for area overlap for added randomness.
    """
    _AREA_TILES = ["floor"]

    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        self.level_budget = level_budget
        self._walk_path()
        self._trim_excess_tiles(self._AREA_TILES)
        self.draw(debug=True)
        return GeneratorOutput(tiles=self._tiles, entities=self._entities)

    # TODO remove test function
    def fake_gen(self, tp=160):
        l = LevelBudget(monster_pool=[], entity_points=tp, tile_points=tp, area_pool=[SquareRoom], area_weight=[1])
        return self.generate(l)

    def _get_area_monster_pool(self):
        return self.level_budget.monster_pool

    def _get_layout_directions(self, empty_map: List[List[str]], direction: int,
                               wall_padding: int = 30) -> Tuple[Tuple[int, int], Tuple[int, int], List[int]]:
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
            split_at = random.choice(range(min_area_path, area_count - min_area_path + 1))
            return [area_points_list[0:split_at], area_points_list[split_at:area_count]]

    def _walk_path(self):
        # --- area_generators init
        area_points_list = self._get_area_points()
        entity_points_list = self._get_entity_points(area_points_list)
        self._tiles = self._get_empty_map(sum(area_points_list))
        area_generators: List[Type[AreaGenerator]] = self._get_area_generators(len(area_points_list))

        # --- setup map layout directions
        map_dir = random.choice([0, 1, 2, 3])  # up, right, down, left
        start, end, sideways_directions = self._get_layout_directions(self._tiles, map_dir)
        sideways_directions.sort(reverse=bool(random.getrandbits(1)))  # randomizes which direction first path takes

        # --- decide which areas goes in which path
        min_area_path = 4
        paths = self._get_path_areas(area_points_list, min_area_path)
        # len_main_path determines how long BOTH parallel paths are going to be - any excess will be side-areas
        # TODO make side areas a random small fraction of the total rather than complete random
        len_main_path = random.choice(range(min_area_path, min(map(len, paths)) + 1))  # + 1 as range is inkl->excl

        # --- generate path by path
        # to keep track of generated sources (top-left offset, entry-direction, prev-area index, result)
        area_history: List[Tuple[Tuple[int, int], int, int, Type[GeneratorOutput]]] = []
        area_cntr, end_path_starting_area_i = 0, None  # indexes to "areas" above
        can_take_mid = True
        for idx, path_area_points_list in enumerate(paths):
            if idx == len(paths) - 1:
                end_path_starting_area_i = area_cntr
            outward_dir = sideways_directions[idx % 2]
            inward_dir = sideways_directions[(idx + 1) % 2]
            has_gone_outward, has_gone_inward = False, False
            side_areas_left = len(path_area_points_list) - len_main_path  # TODO does not distinguish for this yet
            pos = start
            # print("PATH / sides", idx, side_areas_left)

            # --- sometimes a path will start off NOT going outwards directly
            if can_take_mid and bool(random.getrandbits(1)):
                current_dir = map_dir
            else:
                has_gone_outward = True
                current_dir = outward_dir
            can_take_mid = False  # only starting path can take mid

            # --- generate path areas
            force_forward = 0
            for idy, points in enumerate(path_area_points_list):
                # TODO make last room in first path have a chance to be a reward-type room (last room in 2nd is exit)
                # print("--- AREA", idy, idx)
                is_end_area = (idx == len(paths) - 1 and idy == len(path_area_points_list) - 1)
                if area_cntr == 0:
                    level_connect_number = self.level_budget.level_number - 1
                elif is_end_area:
                    level_connect_number = self.level_budget.level_number + 1
                else:
                    level_connect_number = -1
                area_budget = AreaBudget(tile_points=area_points_list[area_cntr],
                                         doorways=[])  # we don't ask to gen doors, as we will open them up from here
                entity_budget = EntityBudget(entity_points=entity_points_list[area_cntr],
                                             monster_pool=self._get_area_monster_pool(),
                                             level_connect_number=level_connect_number)
                area_output = area_generators[area_cntr]().generate(entity_budget=entity_budget,
                                                                    area_budget=area_budget)

                # --- set new pos depending on previous (except for start area)
                # "flip" - aligning rooms in a 2-path scenario, to avoid overlap on "middle" I hang them "outwards"
                # which can otherwise be a problem if the new room is wider/taller than the previous one
                area_w, area_h, pad = len(area_output.tiles), len(area_output.tiles[0]), 1
                # print("DIRECTION W/H -", current_dir, area_w, area_h)
                if area_cntr == 0:
                    # no offset calc for first area
                    self._merge_area(area_output, pos)
                else:
                    x_offset, y_offset = None, None
                    prev_pos = pos
                    prev_area = area_history[area_cntr - 1] if idy != 0 else area_history[0]  # roll-back to start
                    prev_area_w, prev_area_h = len(prev_area[3].tiles), len(prev_area[3].tiles[0])

                    # --- checking-vars for previous area collision (as reduced as I could think of)
                    # since its so reduced, we will generate overlapping areas here and there (a nice amount =)
                    top_left = self._tiles[pos[0] - 2][pos[1] - 2]
                    top_right = self._tiles[pos[0] + prev_area_w + 1][pos[1] - 2]
                    bot_left = self._tiles[pos[0] - 2][pos[1] + prev_area_h + 1]
                    bot_right = self._tiles[pos[0] + prev_area_w + 1][pos[1] + prev_area_h + 1]

                    # TODO remove collision corners debug output
                    """
                    self._tiles[pos[0] - 2][pos[1] - 2] = str(area_cntr)
                    self._tiles[pos[0] + prev_area_w + 1][pos[1] - 2] = str(area_cntr)
                    self._tiles[pos[0] - 2][pos[1] + prev_area_h + 1] = str(area_cntr)
                    self._tiles[pos[0] + prev_area_w + 1][pos[1] + prev_area_h + 1] = str(area_cntr)
                    """

                    # --- calculate new area top-left coordinate based on a previous area
                    # directions: 0, 1, 2, 3 - up, right, down, left
                    if current_dir == 0 or current_dir == 2:
                        y_offset = -(area_h + pad) if current_dir == 0 else prev_area_h + pad
                        l, r = (top_left, top_right) if current_dir == 0 else (bot_left, bot_right)
                        # now we decide on side-ways alignment for the new area; naively, as we only check a few tiles
                        if l in self._AREA_TILES:  # left is already used by an area, can't go there
                            x_offset = random.choice(range(0, prev_area_w - 1))
                        elif r in self._AREA_TILES:
                            x_offset = random.choice(range(-(area_w - 1), prev_area_w - area_w))
                        else:  # both sides should be free of existing areas
                            x_offset = random.choice(range(-(area_w - 1), prev_area_w - 1))
                    elif current_dir == 1 or current_dir == 3:
                        x_offset = prev_area_w + pad if current_dir == 1 else -(area_w + pad)
                        t, b = (top_right, bot_right) if current_dir == 1 else (top_left, bot_left)
                        if t in self._AREA_TILES:
                            y_offset = random.choice(range(0, prev_area_h - 1))
                        elif b in self._AREA_TILES:
                            y_offset = random.choice(range(-(area_h - 1), prev_area_h - area_h))
                        else:
                            y_offset = random.choice(range(-(area_h - 1), prev_area_h - 1))

                    # --- area merge and add to history
                    # print("PREV x y", pos, x_offset, y_offset)
                    pos = pos[0] + x_offset, pos[1] + y_offset
                    # print("MERGE AT", pos)
                    self._merge_area(area_output, pos)

                    # --- change tiles between areas to "open doors"
                    prev_area_rect = Rect(prev_pos, prev_area_w, prev_area_h)
                    area_rect = Rect(pos, area_w, area_h)
                    self._connect_areas(prev_area_rect, area_rect,
                                        new_tile_name=self._AREA_TILES[0],
                                        mutable_tile_names=[self._EMPTY_TILE])

                # self._tiles[pos[0]][pos[1]] = area_cntr  # area debug labeling
                area_history.append((pos, current_dir, area_cntr, area_output))

                # --- control path turning direction
                if idy == 0:
                    force_forward = 1
                    current_dir = map_dir
                elif is_end_area:
                    # --- attempt to connect paths on near-end areas - only 1 additional connection
                    connection_coords = False
                    for first_area in area_history[-1:end_path_starting_area_i - 1:-1]:
                        for second_area in reversed(area_history[:3]):
                            if not connection_coords:
                                first_area_rect = Rect(first_area[0], len(first_area[3].tiles),
                                                       len(first_area[3].tiles[0]))
                                second_area_rect = Rect(second_area[0], len(second_area[3].tiles),
                                                        len(second_area[3].tiles[0]))
                                connection_coords = self._connect_areas(first_area_rect, second_area_rect,
                                                                        new_tile_name=self._AREA_TILES[0],
                                                                        mutable_tile_names=[self._EMPTY_TILE],
                                                                        must_connect=False)
                else:
                    if force_forward > 0:
                        force_forward -= 1
                        current_dir = map_dir
                    else:
                        force_forward = 1
                        if random.random() < (idy + 1) / len(path_area_points_list):
                            if not has_gone_outward:  # before 50% we will turn outwards
                                has_gone_outward = True
                                current_dir = outward_dir
                            elif not has_gone_inward:  # after 50% and before 100% we will turn inwards
                                has_gone_inward = True
                                current_dir = inward_dir
                        else:
                            current_dir = map_dir
                area_cntr += 1
