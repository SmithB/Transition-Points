from shapely import Point

import Conversions
import Point as Pt


TOLERANCE = 10  # roughly .0100 km


def validate_points(segments):
    i = 0
    while i < len(segments):
        num_points = len(segments[i].points)
        print(i)

        if i == len(segments) - 1:
            if 0 < num_points <= 2:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i - 1] = push_up(segments[i - 1])
                        segments[i].points.pop(0)
                        break
                    else:
                        # Not too sure tbh
                        print('ERROR 8')
                        break
                else:
                    if num_points == 1:
                        if segments[i].state.value == segments[i].points[0].state.value:
                            print('ERROR 9')
                        else:
                            break
            elif num_points == 0:
                break
            else:
                print('ERROR 13')
                break

        if num_points == 1:
            if i > 0:
                # print(len(segments[i].points))
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
                            segments[i].points.pop()
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
                        segments[i].points.pop()
                        segments[i] = push_up(segments[i])
                    else:
                        print('ERROR 2')
            else:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments) - 1:
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].points.pop()
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
                            segments[i].points.pop()
                            segments[i] = push_up(segments[i])
                            continue
                        else:
                            print('ERROR 4')
            elif i == 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this points transitions for this segment
                    segments[i + 1].points.insert(0, segments[i].points[-1])
                    segments[i].points.pop()
                    segments[i] = push_up(segments[i])
                    continue
                else:
                    if i < len(segments) - 1:
                        segments[i + 1].points.insert(0, segments[i].points[-1])
                        segments[i].points.pop()
                        segments[i] = push_up(segments[i])
                        continue
                    else:
                        print('ERROR 5')
            else:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        segments[i - 1] = push_up(segments[i - 1])
                        continue
                    else:
                        print('ERROR 6')
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments[i].points) - 1:
                        segments[i + 1].insert(0, segments[i].points[-2])
                        segments[i + 1].insert(0, segments[i].points[-1])
                        segments[i].points.pop()
                        segments[i].points.pop()
                        segments[i] = push_up(segments[i])
                        continue
                    else:
                        segments[i].points.pop()
                        segments[i].points.pop()
                        segments[i] = push_up(segments[i])
                        # print('ERROR 7')
                else:
                    segments[i].points = segments[i].points  # Delete the points, hope the next segment has extra point

        elif num_points == 4:
            if i > 1:
                if len(segments[i - 1].points) == 0:
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i - 1] = push_up(segments[i - 1])
                        segments[i].points.pop(0)
                        continue
                    else:
                        print('ERROR 10')
                elif i < len(segments) - 1:
                    if len(segments[i + 1].points) == 0:
                        if segments[i].points[-1].state.value == segments[i].state.value:
                            segments[i + 1].points.append(segments[i].points[-1])
                            segments[i + 1] = push_up(segments[i + 1])
                            segments[i].points.pop()
                            continue
                else:
                    print('ERROR 11')
        else:
            print('ERROR 12')
        i += 1

    return segments


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
