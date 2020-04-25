from enum import Enum
TILE_TYPE = Enum('TILE_TYPE', 'wall floor')

class Tile:
    name = ''
    type: TILE_TYPE = None
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
    name = 'wall'
    blocked = True
    block_sight = True


class Floor(Tile):
    name = 'floor'
    blocked = False
    block_sight = False


# match the tiles from map generator to actual tiles
# {'floor': Floor, ...}
TILE_MAP = {tile_class.name: tile_class for tile_class in [Wall, Floor]}
