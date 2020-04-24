from world.rooms.map_generators._map_generator import _MapGenerator

import logging
logger = logging.getLogger(__name__)

W = 'wall'
F = 'floor'
_ = None


class DummyGenerator(_MapGenerator):
    def __init__(self):
        super().__init__()
        self.gen_random()
        self.tiles = self.make()

    def gen_random(self):
        self._layers = [
            [
                [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
                [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
            ],
            [
                [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, W, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, W, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, W, _, _, _, _, _, _, _, _, _, _, _],
                [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
            ],
        ]

        self._player_spawn_areas = [
            [(1, 1), (2, 2)]  # upper left
        ]
        self._monster_spawn_areas = [
            [(5, 7), (6, 8)]  # bottom right
        ]

    def make(self):
        """
        merge all layers into one

        [[W]] becomes [W]
        [[W], [F]] becomes [F]
        [[W], [F], [_]] becomes [F]
        [[W], [F], [_], [W]] becomes [W]

        :return: 
        """
        tmp = [' ']
        # inflate result map with Nones
        first_layer = self._layers[0]
        tmp = tmp * len(first_layer[0])  # a row with the length of the first row of the first layer
        result = []
        for x in range(len(first_layer)):
            result.append(tmp.copy())

        for layer in self._layers:
            for row_idx, row in enumerate(layer):
                for col_idx, char in enumerate(row):
                    element_at_index = layer[row_idx][col_idx]
                    if element_at_index:
                        result[row_idx][col_idx] = element_at_index
        return result
