TILE_NAMES = dict(floor="floor", wall="wall")

class Tile:
    name = None
    blocked = False
    block_sight = False

    def __init__(self):
        self.needs_update = True  # true if we need to send this tile as update to the players
        self.is_visible = False
        self.seen = False

    def serialize_attributes(self):
        """
        serialize the stuff the client needs to know about this tile

        :return: 
        """
        return self.seen, self.is_visible
        
        
class Wall(Tile):
    name = TILE_NAMES["floor"]
    blocked = True
    block_sight = True


class Floor(Tile):
    name = TILE_NAMES["wall"]
    blocked = False
    block_sight = False


# match the tiles from map generator to actual tiles
# {'floor': Floor, ...}
TILE_MAP = {tile_class.name: tile_class for tile_class in [Wall, Floor]}
