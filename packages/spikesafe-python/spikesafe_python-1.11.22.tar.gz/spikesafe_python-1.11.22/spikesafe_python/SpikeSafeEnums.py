from enum import IntEnum

class LoadImpedance(IntEnum):
    """
    Load impedance options for the SpikeSafe
    """
    VERY_LOW = 4
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class RiseTime(IntEnum):
    """
    Rise time options for the SpikeSafe
    """
    VERY_SLOW = 4
    SLOW = 3
    MEDIUM = 2
    FAST = 1
