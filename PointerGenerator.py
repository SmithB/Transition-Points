import shapely

from Segment import Segment, State
import Conversions
import Intersections
from shapely import LineString, MultiLineString
# Rules:
#


MIN_TRANSITION_DIST = 1100  # Kilometers

#  Line_segments = []  # list of Segments


# def clean_geometry(geometry, tolerance=1e-9):
#     return geometry.buffer(tolerance).buffer(-tolerance)
#
#
# def validate_segments(segment, polygons):
#     segment_clean = clean_geometry(segment)
#     valid = any(segment_clean.within(polygon))
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
                if state is not state.OCEAN:
                    if rgt.overlaps(intersection):
                        intersection_gcs = LineString(Conversions.cartesian_list_to_gcs(intersection.coords))
                        length = Conversions.get_geodesic_length(intersection_gcs)
                        segment = Segment(intersection, state, length)
                        segments.append(segment)
                else:
                    intersection_gcs = LineString(Conversions.cartesian_list_to_gcs(intersection.coords))
                    length = Conversions.get_geodesic_length(intersection_gcs)
                    segment = Segment(intersection, state, length)
                    print("segment: ", type(segment))
                    segments.append(segment)

    rgt_intersections = Intersections.find_intersections(rgt, rgt_mask)
    print(rgt_intersections)
    if isinstance(rgt_intersections, MultiLineString):
        print(("attempt"))
        rgt_intersections = MultiLineString([segment for segment in rgt_intersections.geoms if segment.dwithin(rgt, 1e-8)])
        print("RGT Intersec: ", rgt_intersections)
    elif isinstance(rgt_intersections, LineString):
        rgt_intersections = LineString([segment for segment in rgt_intersections.geoms if segment.dwithin(rgt, 1e-8)])
    add_segment(rgt_intersections, State.RGT)
    rgt_intersections = MultiLineString([segment.line_string for segment in segments if segment.state == State.RGT])

    land_intersections = Intersections.find_intersections(rgt, land_mask)
    if isinstance(land_intersections, MultiLineString):
        land_intersections = MultiLineString([segment for segment in rgt_intersections.geoms if segment.dwithin(rgt, 1e-8)])
    elif isinstance(land_intersections, LineString):
        land_intersections = LineString([segment for segment in rgt_intersections.geoms if segment.dwithin(rgt, 1e-8)])
    add_segment(land_intersections, State.VEGETATION)
    land_intersections = MultiLineString([segment.line_string for segment in segments if segment.state == State.VEGETATION])

    print("VALIDDDD: ", rgt_intersections.is_valid)
    print(land_intersections.is_valid)
    ocean_intersections = rgt.difference(rgt_intersections)
    ocean_intersections = ocean_intersections.difference(land_intersections)
    ocean_intersections = MultiLineString([line_string for line_string in ocean_intersections.geoms if not line_string.is_closed])
    print("ocean: ", ocean_intersections)
    # ocean_intersections = MultiLineString(list(ocean_intersections.exterior.coords))
    # print("VALID: ", ocean_intersections.is_valid)
    print(type(ocean_intersections))
    print(ocean_intersections)

    add_segment(ocean_intersections, State.OCEAN)
    return segments


def clean_geometry(line_string):
    # return line_string.buffer(0).buffer(0)
    return MultiLineString(line_string.simplify(0.01).buffer(0))
def generate_points(line_segments, curr_transition_points):
    print('No clue for now')
