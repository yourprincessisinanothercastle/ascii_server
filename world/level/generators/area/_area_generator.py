'''
An "area" is a themed generated place on a level, like a specific shape and content,
A square room, a large open area, and so on.
'''
import json

class AreaGenerator:
    def __init__(self):
        self._entities: list[dict] = []
        self._tiles = self.generate()

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
