from Segment import Segment, State
import Conversions
import Intersections
from shapely import LineString
# Rules:
#


MIN_TRANSITION_DIST = 1100  # Kilometers

#  Line_segments = []  # list of Segments


def segmentation(rgt_mask, land_mask, rgt):  # Uses modified land Mask
    segments = []
    # everything needs to CARTESIAN

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

    ocean_intersections = rgt.difference(rgt_mask)
    ocean_intersections = ocean_intersections.difference(land_mask)
    add_segment(ocean_intersections, State.OCEAN)
    return segments


def generate_points(line_segments, curr_transition_points):
    print('No clue for now')
