from dataclasses import dataclass, field
from uuid import UUID

# TODO: evaluate, whether namedtuple or attrs can be more suitable for this use case
# nametuple: no validation possible


@dataclass(frozen=True)
class PlayerConfig:
    '''
    This class represents a Data Transfer Object which can be used to store a player's
    initial state.
    uuid: unique ID of a player
    side: human-readable value of side, where the paddle of a player will be placed at the game's start
    coord_x: starting X coordinate of a player
    coord_y: starting Y coordinate of a player
    eligible_to_start: decides, whether this player may place starting and all the following coordinates of the ball
    '''
    uuid: UUID
    side: str
    coord_x: int
    coord_y: int
    eligible_to_start: bool  # TODO: is not used yet (should be used?) - for now I found a diff. solution

    def __post_init__(self):
        self._validate_side(self.side)

    @staticmethod
    def _validate_side(side):
        '''
        This method checks whether side attribute has a valid value.
        Note: this attribute is there just for better understanding of object by human.
        '''
        if side not in ['left', 'right', 'up', 'down']:
            raise ValueError(
                f'Wrong repr string for position: {side}')
