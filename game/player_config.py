from dataclasses import dataclass
from uuid import UUID

# TODO: evaluate, whether namedtuple or attrs can be more suitable for this use case
# nametuple: no validation possible


@dataclass(frozen=True)
class PlayerConfig:
    '''
    This class represents a Data Transfer Object which can be used to store a player's
    initial state.
    '''
    uuid: UUID
    side: str
    coord_x: int
    coord_y: int

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
