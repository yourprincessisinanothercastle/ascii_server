import logging

from world.creatures.creature import Creature


logger = logging.getLogger(__name__)


class Blob(Creature):
    sprite_name = 'blob'
    ACTION_TIME = dict(
        move=1.,
        attack=.20,
        cooldown=.5
    )

    def __init__(self, x: int = 0, y: int = 0, life: int = 10, damage: int = 5):
        super().__init__(x, y,
                         view_radius=10,
                         life=life,
                         damage=damage)
