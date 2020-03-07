from enum import Enum

class Action(Enum):
    # actions are numbered in order of priority, with 0 being the highest priority
    CLOSE_LONG = 0
    CLOSE_SHORT = 1
    OPEN_LONG = 2
    OPEN_SHORT = 3
    NO_ACTION = 4