"""
Module contains functions to reassign and create points for segments when necessary
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""

from shapely import Point, LineString

import Conversions
import Point as Pt
from Segment import State
from Point import TypePoint

# Tolerance represent the threshold to choose between ideal point and original point
TOLERANCE = 1000  # km

OPTIMIZED = True  # Uses original transition points if ideal point is within tolerance


def validate_points(segments, rgt: int):
    """
    Function
    :param segments: list of segments for an RGT
    :param rgt: An int representing the RGT number
    :return: list of segments with points more correctly assigned
    """
    i = 0
    while i < len(segments):
        num_points = len(segments[i].points)

        if i == len(segments) - 1:  # last segment
            if 0 < num_points <= 2:
                if len(segments[i - 1].points) == 0:
                    # Donates a point to the previous segment
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        push_up(segments[i - 1])
                        segments[i].points.pop(0)
                        break
                    else:
                        break
                else:
                    if num_points == 1:
                        if segments[i].state.value == segments[i].points[0].state.value:
                            # The point does not match the required state
                            segments[i].points = []
                            break
                        else:
                            # The point is not an endpoint of the segment
                            segments[i].points[0].endpoint = False
                            break
                    else:
                        segments[i].points = []
                        break
            elif num_points == 0:
                break  # Assumes there is not state change between RGTs
            else:
                segments[i].points = []  # Delete them
                break

        if num_points == 1:
            if i > 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # If the state of point and segment match
                    if len(segments[i - 1].points) < 2:  # Accounts for cases where the first segment needs two points
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                else:
                    push_up(segments[i])
            else:
                if segments[i].points[0].state.value != segments[i].state.value:
                    # If the state of point and segment do not match
                    push_up(segments[i])

                else:
                    # The point is not an endpoint of the segment
                    segments[i].points[0].endpoint = False

        elif num_points == 2:
            if i == 1:
                if len(segments[0].points) < 2:
                    # If the state of point and segment match
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                if i < len(segments) - 1:
                    # If the state of point and segment match
                    if segments[i].points[1].state.value == segments[i].state.value:
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].points.pop()
                        continue
            elif i == 0:
                # If the state of point and segment match
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this point transitions for this segment
                    segments[i].points[0].endpoint = False
                else:
                    if i < len(segments) - 1:
                        # If the state of point and segment match
                        if segments[i].points[1].state.value == segments[i].state.value:
                            # Gives point to next segment
                            segments[i + 1].points.insert(0, segments[i].points[1])
                            segments[i].points.pop()
                            push_up(segments[i])
                    else:
                        segments[i].points = []  # Deletes two points as it assumes no state change
            else:
                if len(segments[i - 1].points) == 0:
                    # If the state of point and segment match
                    if segments[i].state.value == segments[i].points[0].state.value:
                        # Donates point to prev segment
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments) - 1:
                        # Gives point to next segment
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].points.pop()
                        continue
                    else:
                        segments[i].points = []  # Deletes two points as it assumes no state change
                else:
                    segments[i].points = []  # Delete the points, hope the next segment has an extra point

        elif num_points == 3:
            if i == 1:
                if len(segments[0].points) < 2:
                    # If the state of point and segment match
                    if segments[i].points[0].state.value == segments[i].state.value:
                        # Donates point to prev segment
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                    else:
                        if i < len(segments) - 1:
                            # Moves two points to the next segment and removes them from current segment
                            segments[i + 1].points.insert(0, segments[i].points[-1])
                            segments[i + 1].points.insert(0, segments[i].points[-2])
                            segments[i].points.pop()
                            segments[i].points.pop()
                            continue
                else:
                    # If the state of point and segment do not match
                    if segments[i].state.value != segments[i].points[0].state.value:
                        if i < len(segments[i].points) - 1:
                            # Moves two points to the next segment and removes them from current segment
                            segments[i + 1].points.insert(0, segments[i].points[-1])
                            segments[i + 1].points.insert(0, segments[i].points[-2])
                            segments[i].points.pop()
                            segments[i].points.pop()
                            continue
                        else:
                            # Deletes the points
                            segments[i].points.pop()
                            segments[i].points.pop()
                            continue

            elif i == 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this points transitions for this segment
                    segments[i + 1].points.insert(0, segments[i].points[-1])
                    segments[i].points.pop()
                    continue
                else:
                    if i < len(segments) - 1:
                        # Moves two points to the next segment and removes them from current segment
                        segments[i + 1].points.insert(0, segments[i].points[-1])
                        segments[i + 1].points.insert(0, segments[i].points[-2])
                        segments[i].points.pop()
                        segments[i].points.pop()
                        continue
            else:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        # Donates point to prev segment
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments[i].points) - 1:
                        # Moves two points to the next segment and removes them from current segment
                        segments[i + 1].insert(0, segments[i].points[-1])
                        segments[i + 1].insert(0, segments[i].points[-2])
                        segments[i].points.pop()
                        segments[i].points.pop()
                        continue
                    else:
                        # Removes two points from segment
                        segments[i].points.pop()
                        segments[i].points.pop()
                        continue
                else:
                    segments[i].points = []  # Delete the points, hope the next segment has extra point
        else:
            # Deletes points to simplify algorithm if there is too many
            if num_points != 0:
                segments[i].points = []

        if i > 0:
            # Creates point
            if len(segments[i - 1].points) == 0:
                state = TypePoint.VEGETATION
                if segments[i].state == State.RGT:
                    state = TypePoint.RGT
                segments[i - 1].points.append(Pt.Point(rgt, state, 0, 0, created=True))
                push_up(segments[i - 1])

        i += 1

    # Creates point
    if len(segments[len(segments) - 2].points) == 0:
        state = TypePoint.VEGETATION
        if segments[i].state == State.RGT:
            state = TypePoint.RGT
        segments[i - 1].points.append(Pt.Point(rgt, state, 0, 0, created=True))
        push_up(segments[i - 1])

    add_endpoint(segments)  # Adds necessary endpoints

    return segments


def push_up(segment):
    """
    Pushes a point up to the endpoint of a segment if the point is very far away
    :param segment: A segment object
    """
    point = Point([segment.points[-1].longitude, segment.points[-1].latitude])
    segment_endpoint = Point(segment.line_string.coords[-1])

    distance = point.distance(segment_endpoint)

    if OPTIMIZED:  # it will use the original point if it is close enough to the endpoint of the segment
        point_x, point_y = Conversions.cartesian_to_gcs(point.coords[0][0], point.coords[0][1])
        endpoint_x, endpoint_y = Conversions.cartesian_to_gcs(
                                    segment_endpoint.coords[0][0], segment_endpoint.coords[0][1])
        distance = Conversions.get_geodesic_length(LineString(((point_x, point_y), (endpoint_x, endpoint_y))))
        if point_y == 0:
            distance = float('inf')

    if distance > TOLERANCE:
        # Creates a point at the endpoint of the segment
        new_x = list(segment_endpoint.coords)[0][0]
        new_y = list(segment_endpoint.coords)[0][1]

        segment.points[-1] = Pt.Point(segment.points[-1].rgt, segment.points[-1].state, new_y, new_x,
                                      segment.points[-1].asc_req, created=segment.points[-1].created)


def add_endpoint(segments):
    """
    Creates points if any segments (besides the last) lack an endpoint
    :param segments: list of Segment
    """
    i = 0
    while i < len(segments):
        if len(segments[i].points) == 1:
            point = segments[i].points[0]
            if not point.endpoint:
                state = TypePoint.RGT if point.state == TypePoint.VEGETATION else TypePoint.VEGETATION
                segments[i].points.append(Pt.Point(point.rgt, state, 1, 1, created=True))
                push_up(segments[i])

        i += 1
