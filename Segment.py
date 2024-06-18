from shapely import LineString
from enum import Enum


class State(Enum):
    RGT = 0
    VEGETATION = 1
    OCEAN = 2


class Segment:

    def __init__(self, line_string: LineString, state: State, length: float):
        """

        :param line_string: LineString object
        :param state: Represents if this line segment is RGT or Vegetation Pointing
        :param length: Geodesic length of line in km
        """
        self.line_string = line_string
        self.state = state
        self.length = length
