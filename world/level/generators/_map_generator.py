import json

'''
map generators should be accessed via as_json

TODO: does it make sense to do it this way?
'''

class _MapGenerator:
    def __init__(self):
        self.tiles = None
        '''TODO '''
        self._player_spawn_areas = []
        self._monster_spawn_areas = []
        self._items = []

    def draw(self):
        chars = dict(
            wall='#',
            floor='.'
        )
        for row_idx, row in enumerate(self.tiles):
            drawn_row = [chars[tile] for tile in row]
            print(''.join(drawn_row))

    def get_map(self):
        return dict(
            tiles=self.tiles,
            player_spawn_areas=self._player_spawn_areas,
            monster_spawn_areas=self._monster_spawn_areas,
            items=[],
        )

    def as_json(self):
        return json.dumps(self.get_map())
