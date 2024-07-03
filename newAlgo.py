from shapely import Point

import Conversions
import Point as Pt


TOLERANCE = 10  # roughly .0100 km


def validate_segments(segments):
    i = 0
    while i < len(segments):
        num_points = len(segments[i].points)

        if num_points == 1:
            if i > 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    if len(segments[i - 1].points) < 2: # Accounts for cases where the first segment needs two points
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop()
                        segments[i - 1] = push_up(segments[i - 1])
                else:
                    segments[i] = push_up(segments[i])
            else:
                if segments[i].points[0].state.value != segments[i].state.value:
                    segments[i] = push_up(segments[i])

        elif num_points == 2:
            if i == 1:
                if len(segments[0].points) < 2:
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                        continue
                    else:
                        if i < len(segments) - 1:
                            segments[i + 1].points.insert(0, segments[i].points[1])
                            segments[i].pop()
                            segments[i] = push_up(segments[i])
                        else:
                            print('ERROR 1')
            elif i == 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this points transitions for this segment
                    segments[i] = push_up(segments[i])
                else:
                    if i < len(segments) - 1:
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].pop()
                        segments[i] = push_up(segments[i])
                    else:
                        print('ERROR 2')
            else:
                if len(segments[i - 1]) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments[i]) - 1:
                        segments[i + 1].insert(0, segments[i].points[1])
                        segments[i].pop()
                        segments[i] = push_up(segments[i])
                    else:
                        print('ERROR 3')
                else:
                    segments[i].points = []  # Delete the points, hope the next segment has an extra point

        elif num_points == 3:
            if i == 1:
                if len(segments[0].points) < 2:
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                        continue
                    else:
                        if i < len(segments) - 1:
                            segments[i + 1].points.insert(0, segments[i].points[-1])
                            segments[i].pop()
                            segments[i] = push_up(segments[i])
                            continue
                        else:
                            print('ERROR 4')
            elif i == 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this points transitions for this segment
                    segments[i + 1].points.insert(0, segments[i].points[-1])
                    segments.points.pop()
                    segments[i] = push_up(segments[i])
                    continue
                else:
                    if i < len(segments) - 1:
                        segments[i + 1].points.insert(0, segments[i].points[-1])
                        segments[i].pop()
                        segments[i] = push_up(segments[i])
                        continue
                    else:
                        print('ERROR 5')
            else:
                if len(segments[i - 1]) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                        continue
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments[i]) - 1:
                        segments[i + 1].insert(0, segments[i].points[-1])
                        segments[i].pop()
                        continue
                    else:
                        print('ERROR 3')
                else:
                    segments[i].points = segments[i].points  # Delete the points, hope the next segment has an extra point




def push_up(segment):
    point = Point([segment.points[-1].longitude, segment.points[-1].latitude])
    segment_endpoint = Point(segment.line_string.coords[-1])

    # TODO create LineString and calculate distance that way

    if point.distance(segment_endpoint) > TOLERANCE:
        new_x = list(segment_endpoint.coords)[0][0]
        new_y = list(segment_endpoint.coords)[0][1]

        segment.points[-1] = Pt.Point(segment.points[-1].rgt, segment.points[-1].state, new_x, new_y, segment.points[-1].asc_req)
    else:
        print('meets tolerance')

    return segment
