from shapely import Point, LineString

import Conversions
import Point as Pt
from Segment import State
from Point import TypePoint


TOLERANCE = 1000  # km

OPTIMIZED = True


def validate_points(segments, rgt):
    i = 0
    while i < len(segments):
        num_points = len(segments[i].points)
        print(i, num_points, segments[i].state)

        if i == len(segments) - 1:
            if 0 < num_points <= 2:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        push_up(segments[i - 1])
                        segments[i].points.pop(0)
                        break
                    else:
                        # print('add point')
                        # print(segments[i].state.value, segments[i].points[0].state.value)
                        # # Not too sure tbh
                        # segments[i].points = []
                        print('ERROR 8')
                        break
                else:
                    if num_points == 1:
                        if segments[i].state.value == segments[i].points[0].state.value:
                            segments[i].points = []
                            # print('ERROR 9')
                            break
                        else:
                            segments[i].points[0].endpoint = False
                            break
                    else:
                        segments[i].points = []
                        # print('ERROR 15')
                        break
            elif num_points == 0:
                break
            else:
                segments[i].points = []  # Delete them
                print('ERROR 13')
                break

        if num_points == 1:
            if i > 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    if len(segments[i - 1].points) < 2:  # Accounts for cases where the first segment needs two points
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                else:
                    push_up(segments[i])
            else:
                if segments[i].points[0].state.value != segments[i].state.value:
                    push_up(segments[i])

                else:
                    segments[i].points[0].endpoint = False

        elif num_points == 2:
            if i == 1:
                if len(segments[0].points) < 2:
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                if i < len(segments) - 1:
                    if segments[i].points[1].state.value == segments[i].state.value:
                        print("pushed forward")
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].points.pop()
                        continue
            elif i == 0:
                if segments[i].points[0].state.value == segments[i].state.value:
                    # This means this point transitions for this segment
                    # push_up(segments[i])
                    segments[i].points[0].endpoint = False
                else:
                    if i < len(segments) - 1:
                        if segments[i].points[1].state.value == segments[i].state.value:
                            segments[i + 1].points.insert(0, segments[i].points[1])
                            segments[i].points.pop()
                            push_up(segments[i])
                    else:
                        segments[i].points = []  # Deletes two points as it assumes no state change
                        # print('ERROR 2')
            else:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments) - 1:
                        segments[i + 1].points.insert(0, segments[i].points[1])
                        segments[i].points.pop()
                        continue
                    else:
                        segments[i].points = []  # Deletes two points as it assumes no state change
                        # print('ERROR 3')
                else:
                    segments[i].points = []  # Delete the points, hope the next segment has an extra point

        elif num_points == 3:
            if i == 1:
                if len(segments[0].points) < 2:
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                    else:
                        if i < len(segments) - 1:
                            segments[i + 1].points.insert(0, segments[i].points[-1])
                            segments[i + 1].points.insert(0, segments[i].points[-2])
                            segments[i].points.pop()
                            segments[i].points.pop()
                            continue
                        else:
                            print('ERROR 4')
                else:
                    if segments[i].state.value != segments[i].points[0].state.value:
                        if i < len(segments[i].points) - 1:
                            segments[i + 1].points.insert(0, segments[i].points[-1])
                            segments[i + 1].points.insert(0, segments[i].points[-2])
                            segments[i].points.pop()
                            segments[i].points.pop()
                            continue
                        else:
                            segments[i].points.pop()  # Deletes the points
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
                        segments[i + 1].points.insert(0, segments[i].points[-1])
                        segments[i + 1].points.insert(0, segments[i].points[-2])
                        segments[i].points.pop()
                        segments[i].points.pop()
                        continue
                    else:
                        print('ERROR 5')
            else:
                if len(segments[i - 1].points) == 0:
                    if segments[i].state.value == segments[i].points[0].state.value:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop(0)
                        push_up(segments[i - 1])
                        continue
                    else:
                        print('ERROR 6')  # Rendering issue???
                elif segments[i].state.value != segments[i].points[0].state.value:
                    if i < len(segments[i].points) - 1:
                        segments[i + 1].insert(0, segments[i].points[-1])
                        segments[i + 1].insert(0, segments[i].points[-2])
                        segments[i].points.pop()
                        segments[i].points.pop()
                        continue
                    else:
                        segments[i].points.pop()
                        segments[i].points.pop()
                        # print('pop one')
                        continue
                        # print('ERROR 7')
                else:
                    print('deleted three')
                    segments[i].points = []  # Delete the points, hope the next segment has extra point

        elif num_points == 4:
            segments[i].points = []
            # if i == 1:
            #     if len(segments[0].points) < 2:
            #         if segments[i].points[0].state.value == segments[i].state.value:
            #             segments[i - 1].points.append(segments[i].points[0])
            #             segments[i].points.pop(0)
            #             push_up(segments[i - 1])
            #             continue
            #         else:
            #             if i < len(segments) - 1:
            #                 segments[i + 1].points.insert(0, segments[i].points[-1])
            #                 segments[i + 1].points.insert(0, segments[i].points[-2])
            #                 segments[i].points.pop()
            #                 segments[i].points.pop()
            #                 continue
            #             else:
            #                 print('ERROR 4')
            #     else:
            #         if segments[i].state.value != segments[i].points[0].state.value:
            #             if i < len(segments[i].points) - 1:
            #                 segments[i + 1].points.insert(0, segments[i].points[-1])
            #                 segments[i + 1].points.insert(0, segments[i].points[-2])
            #                 segments[i].points.pop()
            #                 segments[i].points.pop()
            #                 continue
            #             else:
            #                 segments[i].points.pop()  # Deletes the points
            #                 segments[i].points.pop()
            #                 continue
            # if i > 0:
            #     if len(segments[i - 1].points) == 0:
            #         if segments[i].points[0].state.value == segments[i].state.value:
            #             segments[i - 1].points.append(segments[i].points[0])
            #             segments[i - 1] = push_up(segments[i - 1])
            #             segments[i].points.pop(0)
            #             continue
            #         else:
            #             print('ERROR 10')
            #     elif i < len(segments) - 1:
            #         if len(segments[i + 1].points) == 0:
            #             if segments[i].points[-1].state.value == segments[i].state.value:
            #                 segments[i + 1].points.append(segments[i].points[-1])
            #                 segments[i].points.pop()
            #                 continue
            #     else:
            #         print('ERROR 11')
            # else:
            #     print('error 16')
        else:
            if num_points != 0:
                segments[i].points = []
                print('ERROR 12')

        if i > 0:
            if len(segments[i - 1].points) == 0:
                state = TypePoint.VEGETATION
                if segments[i].state == State.RGT:
                    state = TypePoint.RGT
                segments[i - 1].points.append(Pt.Point(rgt, state, 0, 0, created=True))
                push_up(segments[i - 1])

        i += 1

    if len(segments[len(segments) - 2].points) == 0:  # TODO add error checking for if there is only one segment
        state = TypePoint.VEGETATION
        if segments[i].state == State.RGT:
            state = TypePoint.RGT
        segments[i - 1].points.append(Pt.Point(rgt, state, 0, 0, created=True))
        push_up(segments[i - 1])

    add_endpoint(segments)

    return segments


def push_up(segment):
    point = Point([segment.points[-1].longitude, segment.points[-1].latitude])
    segment_endpoint = Point(segment.line_string.coords[-1])

    distance = point.distance(segment_endpoint)

    if OPTIMIZED:
        point_x, point_y = Conversions.cartesian_to_gcs(point.coords[0][0], point.coords[0][1])
        endpoint_x, endpoint_y = Conversions.cartesian_to_gcs(segment_endpoint.coords[0][0], segment_endpoint.coords[0][1])
        distance = Conversions.get_geodesic_length(LineString(((point_x, point_y), (endpoint_x, endpoint_y))))
        if point_y == 0:
            distance = float('inf')

    if distance > TOLERANCE:
        new_x = list(segment_endpoint.coords)[0][0]
        new_y = list(segment_endpoint.coords)[0][1]

        segment.points[-1] = Pt.Point(segment.points[-1].rgt, segment.points[-1].state, new_y, new_x,
                                      segment.points[-1].asc_req, created=segment.points[-1].created)


def add_endpoint(segments):
    i = 0
    while i < len(segments):
        if len(segments[i].points) == 1:
            point = segments[i].points[0]
            if not point.endpoint:
                state = TypePoint.RGT if point.state == TypePoint.VEGETATION else TypePoint.VEGETATION
                segments[i].points.append(Pt.Point(point.rgt, state, 1, 1, created=True))
                push_up(segments[i])

        i += 1
