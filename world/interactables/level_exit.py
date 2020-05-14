from world.entity import Entity, InteractionRules, ENTITY_TYPE, InteractionData


class LevelExit(Entity):
    level_number: int  # if we generate level 2, the exits should be created with a different number (higher or lower)

    HITBOX = [
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
        ['X', 'X', 'X'],
    ]

    def __init__(self, x: int, y: int, level_number: int, interaction_rules: InteractionRules):
        super().__init__(x, y, interaction_rules=interaction_rules, entity_type=ENTITY_TYPE.interact)
        self.level_number = level_number
        self.sprite_name = 'level_exit'

    def _on_interact(self, interaction_event: InteractionRules, data: InteractionData, originator: 'Entity'):
        if originator:
            self.floor.exit_entity(entity=originator,
                                   to_level_nr=self.level_number,
                                   from_level_nr=self.floor.level_number)
