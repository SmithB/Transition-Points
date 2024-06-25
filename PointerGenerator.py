from Segment import Segment, State
import Conversions
import Intersections
from shapely import LineString, MultiLineString, Point
import shapely


MIN_TRANSITION_DIST = 550  # Kilometers


def segmentation(rgt_mask, land_mask, rgt):  # Uses modified land Mask
    """
    Segments the given RGT into sections of veg pointing, rgt pointing,
    and ocean/polar region rgt pointing

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
            print("LINE String occurs")
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
                    segments.append(segment)

    rgt_intersections = Intersections.find_intersections(rgt, rgt_mask)
    add_segment(rgt_intersections, State.RGT)
    rgt_intersections = MultiLineString([segment.line_string for segment in segments if segment.state == State.RGT])

    land_intersections = Intersections.find_intersections(rgt, land_mask)
    add_segment(land_intersections, State.VEGETATION)
    land_intersections = MultiLineString([segment.line_string for segment in segments if
                                          segment.state == State.VEGETATION])

    ocean_intersections = rgt.difference(rgt_intersections)
    ocean_intersections = ocean_intersections.difference(land_intersections)
    ocean_intersections = MultiLineString([line_string for line_string in ocean_intersections.geoms
                                           if not line_string.is_closed and line_string.dwithin(rgt, 1e-8)])

    add_segment(ocean_intersections, State.OCEAN)
    return segments


# TODO look into implementing for all segments -- might not be necessary
def merge_touching_segments(segments):
    """
    Merges ocean line segments that should be connected but were split incorrectly by shapely
    :param segments: list of Segments
    :return: cleaned list of Segments
    """
    mask_segments = [segment for segment in segments if segment.state == State.RGT]
    land_segments = [segment for segment in segments if segment.state == State.VEGETATION]
    ocean_segments = [segment for segment in segments if segment.state == State.OCEAN]

    i = 0
    while i < len(ocean_segments) - 1:
        ocean_segment1 = ocean_segments[i].line_string
        ocean_segment2 = ocean_segments[i + 1].line_string
        if ocean_segment1.touches(ocean_segment2):
            merge_coords = list(ocean_segment1.coords)[:-1] + list(ocean_segment2.coords)
            new_length = ocean_segments[i].length + ocean_segments[i+1].length
            new_segment = Segment(LineString(merge_coords), State.OCEAN, new_length)
            ocean_segments[i] = new_segment
            ocean_segments.pop(i + 1)
        i += 1
    return mask_segments + land_segments + ocean_segments


def sort_segments_by_coordinates(segments, starting_coordinate):
    """
    Sorts segments in order starting from the given starting coordinate
    :param segments: list of Segment objects
    :param starting_coordinate: Tuple of (x, y) Cartesian Coordinates
    :return: list of sorted Segment Objects
    """
    sorted_segments = []
    current_coordinate = starting_coordinate

    while segments:
        next_segment = None
        index = -1
        min_distance = float('inf')
        for i, segment in enumerate(segments):
            line = segment.line_string
            start_dist = Point(current_coordinate).distance(Point(line.coords[0][0], line.coords[0][1]))
            end_dist = Point(current_coordinate).distance(Point(line.coords[-1][0], line.coords[-1][1]))

            if start_dist < min_distance:
                min_distance = start_dist
                next_segment = segment
                index = i
            if end_dist < min_distance:
                min_distance = end_dist
                next_line = LineString(line.coords[::-1])
                next_segment = Segment(next_line, segment.state, segment.length)
                index = i
        if next_segment:
            current_coordinate = next_segment.line_string.coords[-1]
            sorted_segments.append(next_segment)
            segments.pop(index)
        else:
            break
    return sorted_segments


# TODO Add warning somehow when removing segment
def remove_segments_under_thresh(segments):
    """
    Removes line segments that are under the minimum distance threshold
    :param segments: list of Segments
    :return: clean list of Segments
    """
    clean_segments = []

    for segment in segments:
        if segment.length >= MIN_TRANSITION_DIST:
            clean_segments.append(segment)

    return clean_segments


# TODO make sure that segment is overlapping another segment before filtering it out
def remove_insignificant_segments(segments):
    """
    Removes extraneous segments that are inconsequential
    :param segments: list of all Segments
    :return: clean list of Segment objects
    """
    clean_segments = [segment for segment in segments if segment.length > 100]
    return clean_segments


# TODO create this function maybe
# Overlap is minimal, test more and see if the issue really needs to be taken care of or it is fine
def modify_overlaps(segments):  # This might have to be called after remove_insignificant_segments(segments)

    print('todo')


def combine_segments(segment1: Segment, segment2: Segment, state: State):
    """
    Merges two given segments with specified state
    :param segment1: Segment object
    :param segment2: Segment object
    :param state: Specified State
    :return: merge segment
    """
    new_line = shapely.line_merge(segment1.line_string, segment2.line_string)
    new_length = segment1.length + segment2.length
    new_segment = Segment(new_line, state, new_length)
    return new_segment


def generate_ideal_points(segments):
    for segment in segments:
        x = segment.line_string.coords[-1][0]
        y = segment.line_string.coords[-1][1]
        print(f'{Conversions.cartesian_to_gcs(x, y)[0]}, {Conversions.cartesian_to_gcs(x, y)[1]}')


def assign_points(rgt, points_dict, segments):
    """
    Assigns unmodified transition points to the given segment based on it points are a segment
    :param rgt: an int representing the rgt to get transition points from
    :param points_dict: dictionary of (key = rgt): (vals = list of transition points (Points Objects))
    :param segments: list of Segment objects
    :return: list of Segment objects with transition points assigned to them
    """
    for point in points_dict[rgt]:
        temp_point = Point(Conversions.gcs_to_cartesian(point.latitude, point.longitude))
        for segment in segments:
            if shapely.dwithin(temp_point, segment.line_string, 10000):  # 10000 is roughly 10 km
                segment.points.append(point)
                break
    return segments
