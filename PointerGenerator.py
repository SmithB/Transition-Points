from Segment import Segment, State
import Intersections
from shapely import LineString, MultiLineString, Point
import shapely
import Conversions
import Point as Pt

import KmlTester

rgt_num = 0
crossing_rgts = []

MIN_TRANSITION_DIST = 1100  # Kilometers


def split_ani_meridian(rgt):
    # test
    coords = list(rgt.coords)
    segments = []

    global rgt_num
    rgt_num += 1

    i = 1
    while i < len(coords):
        prev_point = coords[i - 1]
        current_point = coords[i]

        if ((prev_point[0] < -170 and current_point[0] > 170) or
                (prev_point[0] > 170 and current_point[0] < -170)):
            crossing_rgts.append(rgt_num)
            first_half = coords[:i]
            coords = coords[i:]
            segments.append(LineString(first_half)) if len(first_half) > 1 else None

        i += 1

    segments.append(LineString(coords)) if len(coords) > 1 else None

    # if len(segments) == 0:
    #     segments = [LineString(coords)]

    return segments


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
            line = LineString(Conversions.cartesian_list_to_gcs(list(intersections.coords)))
            length = Conversions.get_geodesic_length(line)
            # if length == 0.0:
            #     return
            # print('LLen: ', length)
            if state is not state.OCEAN:
                if rgt.overlaps(intersections):
                    segment = Segment(intersections, state, length)
                    segments.append(segment)
            else:
                segment = Segment(intersections, state, length)
                segments.append(segment)
        else:
            for intersection in intersections.geoms:
                if state is not state.OCEAN:
                    if rgt.overlaps(intersection):
                        intersection_gcs = LineString(Conversions.cartesian_list_to_gcs(intersection.coords))
                        length = Conversions.get_geodesic_length(intersection_gcs)
                        # print('lllen: ', length)
                        segment = Segment(intersection, state, length)
                        segments.append(segment)
                else:
                    intersection_gcs = LineString(Conversions.cartesian_list_to_gcs(intersection.coords))
                    length = Conversions.get_geodesic_length(intersection_gcs)
                    # print('lllllen: ', length)
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
    print(type(ocean_intersections))
    if not isinstance(ocean_intersections,LineString):
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
    mask_segments = [segment for segment in segments if segment.state == State.RGT]
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

    mask_segments = merge(mask_segments)
    land_segments = merge(land_segments)
    ocean_segments = merge(ocean_segments)
    return mask_segments + land_segments + ocean_segments


def merge_corresponding_segments(segments):
    i = 0
    while i < len(segments) - 1:
        if segments[i].state == segments[i + 1].state:
            segment1 = segments[i].line_string
            segment2 = segments[i + 1].line_string
            merge_coords = list(segment1.coords)[:-1] + list(segment2.coords)
            print('lengths: ', segments[i].length, segments[i + 1].length)
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
    # print(' coordinate', Conversions.cartesian_to_gcs(current_coordinate[0], current_coordinate[1]))

    while segments:
        next_segment = None
        index = -1
        min_distance = float('inf')
        for i, segment in enumerate(segments):
            line = segment.line_string
            curr_x, curr_y = Conversions.cartesian_to_gcs(current_coordinate[0], current_coordinate[1])

            start_line = LineString((Point(curr_x, curr_y), Point(Conversions.cartesian_to_gcs(line.coords[0][0], line.coords[0][1]))))
            end_line = LineString((Point(curr_x, curr_y), Point(Conversions.cartesian_to_gcs(line.coords[-1][0], line.coords[-1][1]))))

            start_dist = Conversions.get_geodesic_length(start_line)
            end_dist = Conversions.get_geodesic_length(end_line)
            # print(start_dist)
            # print(end_dist)

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
            # print(f' {i} coordinate', Conversions.cartesian_to_gcs(current_coordinate[0], current_coordinate[1]))
            sorted_segments.append(next_segment)
            segments.pop(index)
        else:
            break
    return sorted_segments


# TODO Add warning somehow when removing segment
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
            print('Removing Segment')  # Warning
            coords = list(clean_segments[-1].line_string.coords)
            coords.extend(list(segment.line_string.coords))
            line = LineString(coords)
            length = clean_segments[-1].length + segment.length

            new_segment = Segment(line, clean_segments[-1].state, length)
            clean_segments.pop()
            clean_segments.append(new_segment)
        index += 1

    return clean_segments


# TODO make sure that segment is overlapping another segment before filtering it out
def remove_insignificant_segments(segments):
    """
    Removes extraneous segments that are inconsequential
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
    segments_clean = [segments[0]]

    for i in range(len(segments)):
        if segments[i].state == State.OCEAN:
            segments[i].state = State.RGT

    for i in range(1, len(segments)):
        if segments_clean[-1].state == State.RGT:
            if segments[i].state == State.RGT:
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
    Removes extraneous points that were generated near 180 and -180 degrees longitude
    :param points_dict: dictionary containing the transition points for each rgt
    """
    for rgt in range(1, 1388):
        i = 0
        while i < len(points_dict[rgt]):
            point = points_dict[rgt][i]
            longitude, latitude = Conversions.cartesian_to_gcs(point.longitude, point.latitude)
            if longitude > 179.888:
                if -88 <= latitude <= 88 and point.asc_req == -1:  # turn into constants
                    points_dict[rgt].pop(i)
                    i -= 1
            elif longitude < -179.888:
                if -88 <= latitude <= 88 and point.asc_req == -1:
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
    for i in range(1, 1387):
        # if i == 250:
        #     print(points_dict[i + 1][0].asc_req, points_dict[i][-1].endpoint)
        #     breakpoint()
        if points_dict[i][-1].asc_req == -1 and not points_dict[i + 1][0].endpoint:
            points_dict[i].pop(-1)

        elif (points_dict[i + 1][0].asc_req == -1 and
              (points_dict[i][-1].state == points_dict[i + 1][0].state)):
            points_dict[i + 1].pop(0)


def generate_transition_errors(points_dict):
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


def singular_point_errors(points_dict):
    transition_errors = []

    for rgt in range(1, 1388):
        num_points = len(points_dict[rgt])
        if num_points <= 1:
            transition_errors.append(rgt)

    return transition_errors
