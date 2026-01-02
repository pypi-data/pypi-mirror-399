from enum import Enum


class OpLevel(Enum):
    """OpLevel Enum"""

    Operational = 1
    Degraded = 2
    Partial_Outage = 3
    Full_Outage = 4
