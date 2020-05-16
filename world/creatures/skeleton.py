import logging

from world.creatures.creature import Creature


logger = logging.getLogger(__name__)


class Skeleton(Creature):
    sprite_name = 'skeleton'
    ACTION_TIME = dict(
        move=.1,
        attack=.20,
        cooldown=.50
    )


    HITBOX = [
        [None, None, None, None, None],
        [None, 'X', 'X', 'X', None],
        [None, 'X', 'X', 'X', None],
    ]

    def __init__(self, x: int = 0, y: int = 0, life: int = 15, damage: int = 5):
        super().__init__(x, y,
                         view_radius=10,
                         life=life,
                         damage=damage)
