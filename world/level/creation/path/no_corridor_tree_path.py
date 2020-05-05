import json
import random
from typing import Type, List, Tuple

from world.level.creation.path._path_generator import Rect
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
        self._walk_path()
        return GeneratorOutput(tiles=self._tiles, entities=[], player_spawn_areas=[])

    # TODO remove test function
    def fake_gen(self, tp=160):
        l = LevelBudget(monster_pool=[], entity_points=200, tile_points=tp, area_pool=[SquareRoom], area_weight=[1])
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

    def _merge_area(self, area_output: GeneratorOutput, pos: Tuple[int, int]):
        # TODO also merge entities and whatever else is needed
        print("MERGE AT", pos)
        for idx, col in enumerate(area_output.tiles):
            for idy, tile in enumerate(col):
                self._tiles[pos[0] + idx][pos[1] + idy] = tile

    def draw(self):  # TODO remove debug draw version
        """ preview output """
        chars = dict(
            wall='-',
            floor='.'
        )
        for row_idx, row in enumerate(self._tiles):
            drawn_row = []
            for tile in row:
                try:
                    int(tile)
                    drawn_row.append(str(tile))
                except:
                    drawn_row.append(chars[tile])
            print(''.join(drawn_row))

    def _check_collision(self, rect: Rect):
        pass

    def _walk_path(self):
        # --- area_generators init
        area_points_list = self._get_area_points()
        entity_points_list = self._get_entity_points(area_points_list)
        self._tiles = self._get_empty_map(sum(area_points_list))
        area_generators: List[Type[AreaGenerator]] = self._get_area_generators(len(area_points_list))

        # --- setup map layout directions
        map_dir = 0  # TODO uncomment - random.choice([0, 1, 2, 3])  # up, right, down, left
        start, end, sideways_directions = self._get_layout_directions(self._tiles, map_dir)
        sideways_directions.sort(reverse=bool(random.getrandbits(1)))  # randomizes which direction first path takes

        # --- decide which areas goes in which path
        min_area_path = 4
        paths = self._get_path_areas(area_points_list, min_area_path)
        # len_main_path determines how long BOTH parallel paths are going to be - any excess will be side-areas
        # TODO make side areas a random small fraction of the total rather than complete random
        len_main_path = random.choice(range(min_area_path, min(map(len, paths)) + 1))

        # --- generate path by path
        # area_blocks - generated area outputs and info to join them (top-left offset, entry-direction, prev-area index, result)
        area_history: List[Tuple[Tuple[int, int], int, int, Type[GeneratorOutput]]] = []
        area_cntr, i_start_area, i_end_area = 0, None, None  # indexes to "areas" above
        can_take_mid = True
        for idx, path_area_points_list in enumerate(paths):
            outward_dir = sideways_directions[idx % 2]
            inward_dir = sideways_directions[(idx + 1) % 2]
            has_gone_outward, has_gone_inward = False, False
            side_areas_left = len(path_area_points_list) - len_main_path
            pos = start
            print("PATH / sides", idx, side_areas_left)

            # --- sometimes a path will start off NOT going outwards directly
            if can_take_mid and bool(random.getrandbits(1)):
                print("GOING MID", map_dir)
                can_take_mid = False
                current_dir = map_dir
            else:
                print("GOING OUTWARD", map_dir)
                has_gone_outward = True
                current_dir = outward_dir

            # --- generate path areas
            force_forward = 0
            for idy, points in enumerate(path_area_points_list):
                print("--- AREA", idy, idx)
                area_budget = AreaBudget(tile_points=area_points_list[area_cntr],
                                         doorways=[])  # we don't ask to gen doors, as we will open them up from here
                entity_budget = EntityBudget(entity_points=entity_points_list[area_cntr],
                                             monster_pool=self._get_area_monster_pool(),
                                             has_exit=False)
                area_output = area_generators[area_cntr]().generate(entity_budget=entity_budget,
                                                                    area_budget=area_budget,
                                                                    player_spawn_area_count=int(bool(area_cntr == 0)))

                # --- set new pos depending on previous (except for start area)
                # "flip" - aligning rooms in a 2-path scenario, to avoid overlap on "middle" I hang them "outwards"
                # which can otherwise be a problem if the new room is wider/taller than the previous one
                area_w, area_h, pad = len(area_output.tiles), len(area_output.tiles[0]), 1
                print("DIRECTION W/H -", current_dir, area_w, area_h)
                if not area_cntr == 0:  # skip first as we have already set a starting pos
                    x_offset, y_offset = None, None
                    prev_area = area_history[area_cntr - 1][3]
                    prev_area_w, prev_area_h = len(prev_area.tiles[0]), len(prev_area.tiles[0][0])

                    # --- checking for previous area collision
                    top_left = self._tiles[pos[0] - 2][pos[1] - 2]
                    top_right = self._tiles[pos[0] + prev_area_w + 1][pos[1] - 2]
                    bot_left = self._tiles[pos[0] - 2][pos[1] + prev_area_h]
                    bot_right = self._tiles[pos[0] + prev_area_w + 1][pos[1] + prev_area_h + 3]
                    free_tile = "wall"

                    # TODO remove debug output tiles
                    self._tiles[pos[0] - 2][pos[1] - 2] = str(area_cntr)
                    self._tiles[pos[0] + prev_area_w + 1][pos[1] - 2] = str(area_cntr)
                    self._tiles[pos[0] - 2][pos[1] + prev_area_h + 3] = str(area_cntr)
                    self._tiles[pos[0] + prev_area_w + 1][pos[1] + prev_area_h + 3] = str(area_cntr)

                    if current_dir == 0 or current_dir == 2:
                        y_offset = -(area_h + pad) if current_dir == 0 else area_h + pad
                        l, r = (top_left, top_right) if current_dir == 0 else (bot_left, bot_right)
                        if l is not free_tile:
                            x_offset = random.choice(range(0, prev_area_w - 1))
                        elif r is not free_tile:
                            x_offset = random.choice(range(-(area_w - 1), prev_area_w - area_w))
                        else:
                            x_offset = random.choice(range(-(area_w - 1), prev_area_w - 1))
                    # --- directions: 0, 1, 2, 3 - up, right, down, left
                    elif current_dir == 1 or current_dir == 3:
                        x_offset = area_w + pad if current_dir == 1 else -(area_w + pad)
                        t, b = (top_right, bot_right) if current_dir == 1 else (top_left, bot_left)
                        if t is not free_tile:
                            y_offset = random.choice(range(0, prev_area_h - 1))
                        elif b is not free_tile:
                            y_offset = random.choice(range(-(area_h - 1), prev_area_h - area_h))
                        else:
                            y_offset = random.choice(range(-(area_h - 1), prev_area_h - 1))

                    print("old x y", pos, x_offset, y_offset)
                    pos = pos[0] + x_offset, pos[1] + y_offset

                # --- merge and add to history
                self._merge_area(area_output, pos)
                self._tiles[pos[0]][pos[1]] = area_cntr  # TODO remove area debug labeling
                area_history.append((pos, current_dir, area_cntr, area_output))

                #print("area", idy, (idy + 1) / len(path_area_points_list) / 2)

                # --- control path turning direction
                if area_cntr == 0:
                    i_start_area = area_cntr
                    force_forward = 2
                elif area_cntr == len_main_path:
                    i_end_area = area_cntr
                else:
                    # avoiding direction manipulation for first/last room (shared starting-rooms for paths)
                    if force_forward > 0:
                        force_forward -= 1
                        current_dir = map_dir  # after turning, we go forward first before turning again
                    else:
                        force_forward = 2
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

        self._tiles[0][0] = "0"
        print("TIME TO DRAW!!!", len(self._tiles))
        self.draw()
