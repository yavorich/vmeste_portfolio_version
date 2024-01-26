from enum import Enum


class EventState(str, Enum):
    BEFORE = "before"
    WHILE = "while"
    AFTER = "after"
