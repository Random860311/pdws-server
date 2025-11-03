from enum import Enum


class ESystemPriority(int, Enum):
    LEAD = 0
    LAG_1 = 1
    LAG_2 = 2
    LAG_3 = 3
    OUT = 4