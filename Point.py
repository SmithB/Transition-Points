from enum import Enum


class TypePoint(Enum):
    RGT = 0
    VEGETATION = 1


class Point:
    def __init__(self, rgt: int, state: TypePoint, latitude: float, longitude: float):
        self.rgt = rgt
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
