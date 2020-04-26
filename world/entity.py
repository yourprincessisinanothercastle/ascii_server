from enum import Enum

# use one of these for inherited types
ENTITY_TYPE = Enum('ENTITY_TYPE', 'creature item interact exit')


class Entity:
    '''
    something that has coords on a map tile
    '''

    def __init__(self, x, y, entity_type: ENTITY_TYPE):
        self.entity_type: ENTITY_TYPE = entity_type
        self.x = x
        self.y = y
