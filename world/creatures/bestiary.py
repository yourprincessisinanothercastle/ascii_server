from typing import Type, List, NamedTuple
from world.creatures import Creature, Blob, Skeleton


class Appearance(NamedTuple):
    creature_class: Type[Creature]
    price: int  # the entity_point cost for one of these  # TODO not entirely sure this should exist here yet
    weight: int = 100  # relative chance to other monsters or spawning (100 would be base, to allow 1 = 1%)
    minimum_level: int = 1  # which level is the first level you can encounter this monster?
    difficulty_weight: float = 0  # positive = more with higher diff, ex: 0.2 should add 20% of weight, per diff


class Bestiary:
    """
    This class contains utility functions to get a list of monsters with relative weights (chance of appearing)
    """
    # include all monster creatures in here
    _ALL: List[Appearance] = [
        Appearance(creature_class=Blob, minimum_level=1, weight=100, difficulty_weight=-0.3, price=10),
        Appearance(creature_class=Skeleton, minimum_level=2, weight=100, difficulty_weight=-0.2, price=15)
    ]

    @staticmethod
    def get_monster_pool(level_number: int = None,
                         creature_base: List[Appearance] = None) -> List[Appearance]:
        """ Build a list of available creature types - If no subset is present, any creature can be picked """
        if not creature_base:
            creature_base = Bestiary._ALL.copy()

        def f(a: Appearance):
            # TODO allow custom filter parameters to alter the output list
            return a.minimum_level <= level_number

        sub_pool = []
        for appearance in list(filter(f, creature_base)):
            sub_pool.append(appearance)

        return sub_pool
