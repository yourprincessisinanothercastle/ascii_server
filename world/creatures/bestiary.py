from typing import Type, List
from world.creatures import Creature
from world.creatures import Blob

# TODO it would be good to have all monsters indexed with some kind of params - "earliest level possible", "normally not together with X" etc
# TODO probably a setting in Bestiary to avoid cluttering up the creature classes
# TODO this would control the monster pack themes a bit

class Bestiary:
    @staticmethod
    def get_creature_pool(type_subset: List[str] = None) -> List[Type[Creature]]:
        # TODO allow filter parameters to alter the output list
        return [Blob]
