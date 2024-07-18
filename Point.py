from enum import Enum


class TypePoint(Enum):
    RGT = 0
    VEGETATION = 1


class Point:
    def __init__(self, rgt: int, state: TypePoint, latitude: float, longitude: float, asc_req: int = -1,
                 endpoint: bool = True):
        self.rgt = rgt
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
        self.asc_req = asc_req
        self.endpoint = endpoint
