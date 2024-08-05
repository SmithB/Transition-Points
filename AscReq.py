"""
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""

from shapely import LineString, Point

import Conversions


def generate_asc_req(coords, points):
    """
    Function generates ascending requirements for created points
    :param coords: list of GCS coordinates for an RGT
    :param points: list of points for an RGT
    :return:
    """

    # RGT will get broken down into three segments
    segment1 = None
    segment2 = None

    index = 0
    for i in range(len(coords) - 1):
        if coords[i][1] > coords[i + 1][1]:  # Checks the latitudes to find the 90 to -90 change
            segment1 = LineString(Conversions.gcs_list_to_cartesian(coords[:i]))
            index = i + 1
            break

    if segment1:
        for i in range(index, len(coords) - 1):
            if coords[i][1] < coords[i + 1][1]:  # Checks the latitudes to find the -90 to -0 change
                segment2 = LineString(Conversions.gcs_list_to_cartesian(coords[index:i]))
                index = i + 1
                break

    # Remainder of segment becomes segment 3
    segment3 = LineString(Conversions.gcs_list_to_cartesian(coords[index:]))

    for point in points:
        if point.created:
            point_cpy = Point(point.longitude, point.latitude)
            dist1 = point_cpy.distance(segment1) / 1000
            dist2 = point_cpy.distance(segment2) / 1000
            dist3 = point_cpy.distance(segment3) / 1000

            # Compares distance between the point and the three segments
            min_dist = min(dist1, dist2, dist3)

            if min_dist == dist1 or min_dist == dist3:
                point.asc_req = 0  # ascending
            else:
                point.asc_req = 1  # descending

        # point_cpy = Point(point.longitude, point.latitude)
        # dist1 = point_cpy.distance(segment1) / 1000
        # dist2 = point_cpy.distance(segment2) / 1000
        # dist3 = point_cpy.distance(segment3) / 1000
        #
        # # Compares distance between the point and the three segments
        # min_dist = min(dist1, dist2, dist3)
        #
        # if min_dist == dist1 or min_dist == dist3:
        #     point.asc_req = 0  # ascending
        # else:
        #     point.asc_req = 1  # descending

