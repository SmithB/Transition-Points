from shapely import Point
import Point as Pt


TOLERANCE = 100000 # roughly 100 km

# TODO handle case w/ issues with first segment
# ex. 2 points but no prior segment to hand to
# TODO handle case w/ issues with last segment


def validate_points(segments):
    print('segments: ', len(segments))
    for i in range(len(segments)):
        num_points = len(segments[i].points)
        if num_points == 1:
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    print('Warning') # donates it TP hoping that the next segment has two points
                    segments[i - 1].points = segments[i].points[:]
                    segments[i - 1] = push_up(segments[i - 1])
                    segments[i].points.pop()
                else:
                    segments[i] = push_up(segments[i])
        elif num_points == 2:
            if i > 0:
                if len(segments[i - 1].points) == 0:
                    segments[i - 1].points.append(segments[i].points[0])
                    segments[i].points.popleft()
        elif num_points == 3:
            segments[i].points = [segments[i].points[-1]]
            segments[i] = push_up(segments[i])
        else:
            print(num_points)
            print('figure out later')

    return segments


# TODO may need a difference tolerance


def push_up(segment):
    point = Point([segment.points[-1].longitude, segment.points[-1].latitude])
    segment_endpoint = Point(segment.line_string.coords[-1])

    if point.distance(segment_endpoint) > TOLERANCE:
        new_x = list(segment_endpoint.coords)[0][0]
        new_y = list(segment_endpoint.coords)[0][1]
        print('x', new_x)
        print('y', new_y)
        segment.points[-1] = Pt.Point(segment.points[-1].rgt, segment.points[-1].state, new_x, new_y)

    return segment
