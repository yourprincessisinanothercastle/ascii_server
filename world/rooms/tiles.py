class Tile:
    blocked = False
    block_sight = False

    def __init__(self):
        self.is_visible = False
        self.seen = False


class Wall(Tile):
    blocked = True
    block_sight = True


class Floor(Tile):
    blocked = False
    block_sight = False


# match the tiles from map generator to actual tiles
TILE_MAP = {
    'wall': Wall,
    'floor': Floor,
}
