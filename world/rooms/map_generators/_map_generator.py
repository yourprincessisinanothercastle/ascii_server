import json

'''
map generators should be accessed via as_json

todo: does it make sense to do it this way?
'''

class _MapGenerator:
    def __init__(self):
        self.map = None
        self.layers = []
        self._player_spawn_areas = []
        self._monster_spawn_areas = []
        self._items = []

    def draw(self):
        chars = dict(
            wall='#',
            floor='.'
        )
        for row_idx, row in enumerate(self.map):
            drawn_row = [chars[tile] for tile in row]
            print(''.join(drawn_row))

    def as_json(self):
        return json.dumps(dict(
            map=self.map,
            player_spawn_areas=self._player_spawn_areas,
            monster_spawn_areas=self._monster_spawn_areas,
            items=[],
        ))
