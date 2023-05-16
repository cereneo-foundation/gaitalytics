from enum import Enum


class AxesNames(Enum):
    X = "x"
    Y = "y"
    Z = "z"

    @classmethod
    def get_axes_by_index(cls, index):
        if index == 0:
            return cls.X
        elif index == 1:
            return cls.Y
        elif index == 2:
            return cls.Z


ANALOG_VOLTAGE_PREFIX_LABEL = "Voltage."


class SideEnum(Enum):
    """
    Helper enum to define side
    """
    LEFT = "L"
    RIGHT = "R"
