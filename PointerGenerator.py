from Segment import Segment, State
import Conversions
import Intersections
from shapely import LineString
# Rules:
#


MIN_TRANSITION_DIST = 1100  # Kilometers

#  Line_segments = []  # list of Segments


def segmentation(rgt_mask, land_mask, rgt):  # Uses modified land Mask
    """
    Segments the given RGT into sections of
    veg pointing, rgt pointing, and ocean/polar region rgt pointing
    All must use CARTESIAN coordinates
    :param rgt_mask: Polygon/Multipolygon representing the rgt mask
    :param land_mask: Multipolygon representing USABLE land regions
    (shares no overlap with rgt_mask)
    :param rgt: LineString representing the RGT line
    :return: List of Segment objects that represents the rgt broken up
    """
    segments = []

    def add_segment(intersections, state):
        if type(intersections) is LineString:
            length = Conversions.get_geodesic_length(intersections)
            segment = Segment(intersections, state, length)
            segments.append(segment)
        else:
            for intersection in intersections.geoms:
                length = Conversions.get_geodesic_length(intersection)
                segment = Segment(intersection, state, length)
                segments.append(segment)

    rgt_intersections = Intersections.find_intersections(rgt, rgt_mask)
    add_segment(rgt_intersections, State.RGT)

    land_intersections = Intersections.find_intersections(rgt, land_mask)
    add_segment(land_intersections, State.VEGETATION)

    ocean_intersections = rgt.difference(rgt_intersections)
    ocean_intersections = ocean_intersections.difference(land_intersections)
    print(ocean_intersections)
    add_segment(ocean_intersections, State.OCEAN)
    return segments


def generate_points(line_segments, curr_transition_points):
    print('No clue for now')
