"""
Module generates warnings for transition points
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""
from shapely import LineString, Point

import Conversions


def generate_warnings(transition_errors, significant_rgts_under_thresh, points_dict, threshold):
    """
    Creates txt file that lists the warnings and errors

    :param transition_errors: list of RGTs with errors where two consecutive points have the same state
    :param significant_rgts_under_thresh: list of RGTs where segments of significant length where skipped
    :param points_dict: a dictionary containing list of points
    :param threshold: the threshold
    """
    too_close_rgts = check_too_close_points(points_dict)
    rgts_within_thresh = points_within_threshold(points_dict, threshold)
    with open('assets/warnings.txt', 'w') as file:
        file.write('ERRORS:\n')
        for error in set(transition_errors):
            file.write(f'RGT: {error} \n')

        if len(rgts_within_thresh) != 0:
            file.write('Distance Errors:\n')
            for rgt in set(rgts_within_thresh):
                file.write(f'RGT: {rgt}\n')
        file.write("\n\n")

        file.write('WARNINGS:\n')
        file.write('RGTs where large segments under threshold were skipped:\n')
        for rgt in significant_rgts_under_thresh:
            file.write(f'RGT: {rgt}\n')
        file.write("\n")

        file.write('RGTs where there are multiple Transition Points in a 1500 km distance:\n')
        for rgt in too_close_rgts:
            file.write(f'RGT: {rgt}\n')
        file.write('\nGood Luck!')


def check_too_close_points(points_dict):
    """
    Function checks to see which RGTs have three transition points in a 1500 km distance
    :param points_dict: a dictionary containing list of points
    :return: list of rgts with points that are too close together
    """
    too_close_rgts = []

    for rgt in range(1, 1388):
        for i in range(len(points_dict[rgt]) - 2):
            points = points_dict[rgt]
            point1 = Point(Conversions.cartesian_to_gcs(points[i].longitude, points[i].latitude))
            point2 = Point(Conversions.cartesian_to_gcs(points[i + 1].longitude, points[i + 1].latitude))
            point3 = Point(Conversions.cartesian_to_gcs(points[i + 2].longitude, points[i + 2].latitude))
            line = LineString([point1, point2, point3])
            length = Conversions.get_geodesic_length(line)

            if length < 1500:
                too_close_rgts.append(f'{rgt}  Points: {i+1}, {i+2}, {i+3}')

    return too_close_rgts


def points_within_threshold(points_dict, threshold):
    """
    Creates a list of RGTs that have two transition points within the threshold distance

    :param points_dict: a dictionary containing a list of points
    :param threshold: threshold distance in km
    :return: a list of RGTs with two transition points within the threshold distance
    """
    rgts = []

    for rgt in range(1, 1388):
        for i in range(len(points_dict[rgt]) - 1):
            points = points_dict[rgt]
            point1 = Point(Conversions.cartesian_to_gcs(points[i].longitude, points[i].latitude))
            point2 = Point(Conversions.cartesian_to_gcs(points[i + 1].longitude, points[i + 1].latitude))
            line = LineString([point1, point2])
            length = Conversions.get_geodesic_length(line)

            if length < threshold:
                rgts.append(f'{rgt}  Points: {i+1}and {i+2}')

    return rgts
