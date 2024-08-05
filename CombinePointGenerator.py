"""
Module contains functions to convert RGT into Segments and assigns initial original points. Also generates errors.
This function is meant for Off-pointing masks
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""

from Segment import Segment, State
import Intersections
from shapely import LineString, MultiLineString, Point
import shapely
import Conversions
import Point as Pt

# list of RGTs that have segments under the threshold but greater than the warning thresh
significant_rgts_under_thresh = []

curr_rgt = 0  # RGT Counter

MIN_TRANSITION_DIST = None  # Kilometers
WARNING_THRESH = 500  # Kilometers


def split_anti_meridian(rgt):
    """
    Split a rgt into segments when it intersects the antimeridian to avoid antimeridian issues
    :param rgt: A LineString containing coordinates in GCS
    :return: A list of the new segments
    """
    coords = list(rgt.coords)
    segments = []

    global curr_rgt
    curr_rgt += 1

    i = 1
    while i < len(coords):
        prev_point = coords[i - 1]
        current_point = coords[i]

        # Finds the intersection
        if ((prev_point[0] < -170 and current_point[0] > 170) or
                (prev_point[0] > 170 and current_point[0] < -170)):
            first_half = coords[:i]
            coords = coords[i:]
            segments.append(LineString(first_half)) if len(first_half) > 1 else None

        i += 1

    segments.append(LineString(coords)) if len(coords) > 1 else None

    return segments


def segmentation(land_mask, rgt):
    """
    Segments the given RGT into sections of veg pointing, rgt pointing,
    and ocean/polar region rgt pointing. Uses modified land Mask

    All must use CARTESIAN coordinates
    :param rgt_mask: Polygon/Multipolygon representing the rgt mask
    :param land_mask: Multipolygon representing USABLE land regions
    (shares no overlap with rgt_mask)
    :param rgt: LineString representing the RGT line
    :return: List of Segment objects that represents the rgt broken up
    """
    segments = []

    def add_segment(intersections, state):
        """
        Nested function that add segments to list based of intersections and state
        :param intersections: A geometry that is the intersection between two geometries
        :param state: State wanted for segments
        """

        if type(intersections) is LineString:
            line = LineString(Conversions.cartesian_list_to_gcs(list(intersections.coords)))
            length = Conversions.get_geodesic_length(line)

            # Does not check for overlap with ocean segments due to floating-point precision errors
            if state is not state.OCEAN:
                if rgt.overlaps(intersections):
                    segment = Segment(intersections, state, length)
                    segments.append(segment)
            else:
                segment = Segment(intersections, state, length)
                segments.append(segment)
        else:
            # intersection will usually be a MultiLineString
            for intersection in intersections.geoms:
                # Does not check for overlap with ocean segments due to floating-point precision errors
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

    land_intersections = Intersections.find_intersections(rgt, land_mask)
    add_segment(land_intersections, State.VEGETATION)
    land_intersections = MultiLineString([segment.line_string for segment in segments if
                                          segment.state == State.VEGETATION])

    ocean_intersections = rgt.difference(land_intersections)
    if not isinstance(ocean_intersections, LineString):
        ocean_intersections = MultiLineString([line_string for line_string in ocean_intersections.geoms
                                               if not line_string.is_closed and line_string.dwithin(rgt, 1e-8)])
    add_segment(ocean_intersections, State.OCEAN)

    return segments


def merge_touching_segments(segments):
    """
    Merges line segments that should be connected but were split incorrectly by shapely
    :param segments: list of Segments
    :return: cleaned list of Segments
    """
    land_segments = [segment for segment in segments if segment.state == State.VEGETATION]
    ocean_segments = [segment for segment in segments if segment.state == State.OCEAN]

    def merge(segments):
        i = 0
        while i < len(segments) - 1:
            segment1 = segments[i].line_string
            segment2 = segments[i + 1].line_string
            if segment1.touches(segment2):
                merge_coords = list(segment1.coords)[:-1] + list(segment2.coords)
                new_length = segments[i].length + segments[i+1].length
                new_segment = Segment(LineString(merge_coords), State.OCEAN, new_length)
                segments[i] = new_segment
                segments.pop(i + 1)
            i += 1
        return segments

    land_segments = merge(land_segments)
    ocean_segments = merge(ocean_segments)
    return land_segments + ocean_segments


def merge_corresponding_segments(segments):
    """
    Merges segments that were split by the antimeridian
    :param segments: list of Segment
    :return: list of Segments that may have been modified
    """

    i = 0
    while i < len(segments) - 1:
        if segments[i].state == segments[i + 1].state:
            segment1 = segments[i].line_string
            segment2 = segments[i + 1].line_string
            merge_coords = list(segment1.coords)[:-1] + list(segment2.coords)
            new_length = segments[i].length + segments[i + 1].length
            new_segment = Segment(LineString(merge_coords), segments[i].state, new_length)
            segments[i] = new_segment
            segments.pop(i + 1)
            continue

        i += 1

    return segments


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
            curr_x, curr_y = Conversions.cartesian_to_gcs(current_coordinate[0], current_coordinate[1])

            start_line = LineString((Point(curr_x, curr_y),
                                     Point(Conversions.cartesian_to_gcs(line.coords[0][0], line.coords[0][1]))))
            end_line = LineString((Point(curr_x, curr_y),
                                   Point(Conversions.cartesian_to_gcs(line.coords[-1][0], line.coords[-1][1]))))

            start_dist = Conversions.get_geodesic_length(start_line)
            end_dist = Conversions.get_geodesic_length(end_line)

            # Checks both the start distance and end distance to verify that the segment is not backwards
            if start_dist < min_distance:
                min_distance = start_dist
                next_segment = segment
                index = i
            if end_dist < min_distance:
                min_distance = end_dist
                next_line = LineString(line.coords[::-1])  # Reverses coordinates
                next_segment = Segment(next_line, segment.state, segment.length)
                index = i
        if next_segment:
            current_coordinate = next_segment.line_string.coords[-1]
            sorted_segments.append(next_segment)
            segments.pop(index)
        else:
            break
    return sorted_segments


def remove_segments_under_thresh(segments):
    """
    Removes line segments that are under the minimum distance threshold
    Segments must be sorted before use
    :param segments: list of Segments
    :return: clean list of Segments
    """
    clean_segments = []

    index = 0
    last_seg_index = len(segments) - 1
    for segment in segments:
        gcs_coords = Conversions.cartesian_list_to_gcs(list(segment.line_string.coords))
        line = LineString(gcs_coords)
        dist = Conversions.get_geodesic_length(line)
        if dist >= MIN_TRANSITION_DIST or index == 0 or index == last_seg_index:
            clean_segments.append(segment)
        elif clean_segments:
            # Adds a rgt to the list there is a segment greater than the warning thresh
            # but less than the minimum thresh
            if dist > WARNING_THRESH:
                global curr_rgt
                significant_rgts_under_thresh.append(f'{curr_rgt} length: {dist}')

            coords = list(clean_segments[-1].line_string.coords)
            coords.extend(list(segment.line_string.coords))
            line = LineString(coords)
            length = clean_segments[-1].length + segment.length

            new_segment = Segment(line, clean_segments[-1].state, length)
            clean_segments.pop()
            clean_segments.append(new_segment)
        index += 1

    return clean_segments


def remove_insignificant_segments(segments):
    """
    Removes extraneous segments that are inconsequential.
    These segments may have been generated due to floating-point precision issues
    :param segments: list of all Segments
    :return: clean list of Segment objects
    """

    clean_segments = []

    index = 0
    last_seg_index = len(segments) - 1
    for segment in segments:
        gcs_coords = Conversions.cartesian_list_to_gcs(list(segment.line_string.coords))
        line = LineString(gcs_coords)
        dist = Conversions.get_geodesic_length(line)

        # Ignores first and last segments
        if dist >= 100 or index == 0 or index == last_seg_index:
            clean_segments.append(segment)
        index += 1

    return clean_segments


def assign_points(rgt, points_dict, segments):
    """
    Assigns unmodified transition points to the given segment based on it points are a segment
    :param rgt: an int representing the rgt to get transition points from
    :param points_dict: dictionary of (key = rgt): (vals = list of transition points (Points Objects))
    :param segments: list of Segment objects
    :return: list of Segment objects with transition points assigned to them
    """
    for point in points_dict[rgt]:
        cart_coords = Conversions.gcs_to_cartesian(point.latitude, point.longitude)
        temp_point = Point(cart_coords)
        modified_point = Pt.Point(point.rgt, point.state, cart_coords[1], cart_coords[0], point.asc_req)
        for segment in segments:
            if shapely.dwithin(temp_point, segment.line_string, 10000):  # 10000 is roughly 10 km
                segment.points.append(modified_point)
                break

    return segments


def merge_rgt_ocean(segments):
    """
    Function merges rgt and ocean segments if they are next to each other
    :param segments: list of Segments
    :return: list of modified Segments
    """
    segments_clean = [segments[0]]

    for i in range(len(segments)):
        if segments[i].state == State.OCEAN:
            segments[i].state = State.RGT

    for i in range(1, len(segments)):
        if segments_clean[-1].state == State.RGT:
            if segments[i].state == State.RGT:
                # Merges segments
                coords = list(segments_clean[-1].line_string.coords)
                coords.extend(segments[i].line_string.coords)
                new_length = segments_clean[-1].length + segments[i].length
                new_segment = Segment(LineString(coords), State.RGT, new_length)
                segments_clean.pop()
                segments_clean.append(new_segment)
            else:
                segments_clean.append(segments[i])
        else:
            segments_clean.append(segments[i])

    return segments_clean


def remove_twilight_points(points_dict):
    """
    Removes extraneous points that were generated near antimeridian
    :param points_dict: dictionary containing the transition points for each rgt
    """
    for rgt in range(1, 1388):
        i = 0
        while i < len(points_dict[rgt]):
            point = points_dict[rgt][i]
            longitude, latitude = Conversions.cartesian_to_gcs(point.longitude, point.latitude)
            if longitude > 179.888:
                if -33.5 <= latitude <= 4 and point.created:  # These are the bounds of the land mask in that region
                    points_dict[rgt].pop(i)
                    i -= 1
            elif longitude < -179.888:
                if -33.5 <= latitude <= 4 and point.created:  # These are the bounds of the land mask in that region
                    points_dict[rgt].pop(i)
                    i -= 1

            i += 1


def remove_duplicate_points(points_dict):
    """
    Removes Duplicate Points that have no effect on transitions
    :param points_dict: dictionary that contains all transition points
    """
    for rgt in range(1, 1388):
        i = 0
        last_point = None
        while i < len(points_dict[rgt]):
            curr_point = points_dict[rgt][i]
            if last_point is None:
                last_point = points_dict[rgt][i]

            else:
                if last_point.latitude == curr_point.latitude and last_point.longitude == curr_point.longitude:
                    points_dict[rgt].pop(i)
                    points_dict[rgt].pop(i - 1)
                    last_point = None
                    i -= 2

                else:
                    last_point = points_dict[rgt][i]

            i += 1


def remove_extra_endpoints(points_dict):
    """
    Removes unnecessary endpoints that were generated by comparing points with the next RGT
    :param points_dict: dictionary containing list of points
    """
    for i in range(1, 1387):
        if points_dict[i][-1].created and not points_dict[i + 1][0].endpoint and points_dict[i][-1].state == points_dict[i + 1][0].state:
            points_dict[i].pop(-1)

        elif (points_dict[i + 1][0].created and
              (points_dict[i][-1].state == points_dict[i + 1][0].state)):
            points_dict[i + 1].pop(0)


def remove_points_under_threshold(points_dict, threshold):
    """
    Removes a set of points that are under the threshold
    :param points_dict: dictionary containing list of points
    :param threshold: the threshold in Km
    """
    for rgt in range(1, 1388):
        i = 0
        while i < len(points_dict[rgt]) - 1:
            points = points_dict[rgt]
            point1 = Point(Conversions.cartesian_to_gcs(points[i].longitude, points[i].latitude))
            point2 = Point(Conversions.cartesian_to_gcs(points[i + 1].longitude, points[i + 1].latitude))
            line = LineString([point1, point2])  # Creates line between the two points
            length = Conversions.get_geodesic_length(line)
            if length < threshold:
                points_dict[rgt].pop(i + 1)
                points_dict[rgt].pop(i)
                i -= 1
            i += 1


def generate_transition_errors(points_dict):
    """
    Checks for error in RGTs where two consecutive points have the same state
    :param points_dict: dictionary containing lists of points
    :return: a list of RGTs with errors
    """
    transition_errors = []

    last_point = None

    for rgt in range(1, 1388):
        for i in range(len(points_dict[rgt])):
            point = points_dict[rgt][i]
            if last_point is None:
                last_point = point

            else:
                if last_point.state == point.state:

                    if i == 0:
                        transition_errors.append(f'{last_point.rgt} or {rgt}')
                    else:
                        transition_errors.append(f'{rgt}')

                last_point = point

    return transition_errors
