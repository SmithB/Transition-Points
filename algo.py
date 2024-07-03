from shapely import Point

import Conversions
import Point as Pt
from Point import TypePoint
from Segment import State


TOLERANCE = 10  # roughly .0100 km

# TODO handle case w/ issues with first segment
# ex. 2 points but no prior segment to hand to
# TODO handle case w/ issues with last segment


def validate_points(segments):
    print('segments: ', len(segments))
    i = 0
    while i < len(segments):
        print('i: ', i)
        num_points = len(segments[i].points)

        if i == len(segments) - 1:
            # print('needs to be handled differently')
            # # TODO come up with solution
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    if len(segments[i].points) > 0:
                        segments[i - 1].points.append(segments[i].points[0])
                        segments[i].points.pop()
                        segments[i - 1] = push_up(segments[i - 1])
                else:
                    if len(segments[i].points) > 0:
                        print("Warning: Final Segment has a Transition Point")
            break

        if num_points == 1:
            print(1)
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    print('Warning') # donates it TP hoping that the next segment has two points
                    if segments[i].points[0].state.value == segments[i].state.value:
                        segments[i - 1].points = segments[i].points[:]
                        segments[i - 1] = push_up(segments[i - 1])
                        # print(segments[i-1].points[0].latitude,segments[i-1].points[0].longitude)
                        segments[i].points.pop()
                    else:
                        print('Handle this')
                else:
                    print('got here')
                    segments[i] = push_up(segments[i])
            else: # Handles first segment cases
                if segments[i].state.value == segments[i].points[0].state.value:
                    print('do nothing, needs to switch state here')  # maybe push back if anything
                else:
                    print(segments[i].state, segments[i].points[0].state)
                    segments[i] = push_up(segments[i])

        elif num_points == 2:
            print(2)
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    index = find_point(segments[i], segments[i].state.value)
                    if index is None:
                        print('None found')
                        break
                    segments[i - 1].points.append(segments[i].points[index])
                    segments[i - 1] = push_up(segments[i - 1])
                    segments[i].points.pop(index)
                    segments[i] = push_up(segments[i])

                elif i < len(segments) - 1:  # -2 because this prevents the second to last to append a point to the last segment
                    index = find_point(segments[i], segments[i].state.value)
                    if index is None:
                        print('Unfortunate, none found')
                        break
                    if i < len(segments) - 2:
                        segments[i + 1].points.append(segments[i].points[index])
                    segments[i].points.pop(index)
                    segments[i] = push_up(segments[i])

            else:
                if len(segments) > 1:
                    index = find_point(segments[i], segments[i].state.value)
                    if index is None:
                        print("really not sure")
                        break
                    if len(segments[i + 1].points) == 0:
                        segments[i + 1].points.append(segments[i].points[index])
                    segments[i].points.pop(index)
                    segments[i] = push_up(segments[i])
        elif num_points == 3:
            print(3)
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    index = find_point(segments[i], segments[i].state.value)
                    if index is None:
                        print("Nooooooo")
                        break
                    segments[i - 1].points.append(segments[i].points[index])
                    segments[i - 1] = push_up(segments[i - 1])
                    segments[i].points.pop(index)
                    continue

            segments[i].points = [segments[i].points[-1]]  # Essentially removes the first two points
            segments[i] = push_up(segments[i])
        elif num_points == 4:
            print(4)
            # 4+ should not be happening with an upgraded map
            # might have to account for pushing back 1 and then deleting two in the middle

            if i > 0:
                if len(segments[i - 1].points) == 0:
                    segments[i - 1].points.append(segments[i].points[0])
                    segments[i - 1] = push_up(segments[i - 1])
                    segments[i].points = [segments[i].points[-1]]  # removes first two points
                    segments[i] = push_up(segments[i])
                elif i < len(segments) - 1:
                    if len(segments[i + 1].points) == 0:
                        segments[i + 1].points.append(segments[i].points[-1])
                        segments[i].points = [segments[i].points[-1]]  # removes first two points
                        segments[i] = push_up(segments[i])
            else:
                print('Big issue')
        else:
            # 4+ should not be happening with an upgraded map
            print(num_points)
            print('figure out later')

        i += 1

    return segments


# TODO may need a difference tolerance


def push_up(segment):
    point = Point([segment.points[-1].longitude, segment.points[-1].latitude])
    segment_endpoint = Point(segment.line_string.coords[-1])

    # TODO create LineString and calculate distance that way

    if point.distance(segment_endpoint) > TOLERANCE:
        new_x = list(segment_endpoint.coords)[0][0]
        new_y = list(segment_endpoint.coords)[0][1]
        print(Conversions.cartesian_to_gcs(new_x, new_y))

        segment.points[-1] = Pt.Point(segment.points[-1].rgt, segment.points[-1].state, new_x, new_y, segment.points[-1].asc_req)

    return segment


def find_point(segment, state: int):
    for i in range(len(segment.points)):
        if segment.points[i].state.value == state:
            return i
    return None
