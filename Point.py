"""
Module is used to create a Point object
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""
from enum import Enum


class TypePoint(Enum):
    RGT = 0
    VEGETATION = 1


class Point:
    def __init__(self, rgt: int, state: TypePoint, latitude: float, longitude: float, asc_req: int = -1,
                 endpoint: bool = True, created: bool = False):
        self.rgt = rgt
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
        self.asc_req = asc_req
        self.endpoint = endpoint
        self.created = created
