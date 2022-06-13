from enum import Enum

class Direction(Enum):
    """
    Specifies in which direction
    an arrow should point.
    """
    FORWARDS = 0
    BACKWARDS = 1
    BOTH = 3