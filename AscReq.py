from shapely import LineString, Point

import Conversions


def generate_asc_req(coords: LineString, points):

    threshold = 40 # kilometers
    # coords = list(line.coords)

    asc_req = 0

    segment1 = None
    segment2 = None

    index = 0
    for i in range(len(coords) - 1):
        if coords[i][1] > coords[i + 1][1]:
            segment1 = LineString(Conversions.gcs_list_to_cartesian(coords[:i]))
            index = i + 1
            break

    if segment1:
        for i in range(index, len(coords) - 1):
            if coords[i][1] < coords[i + 1][1]:
                segment2 = LineString(Conversions.gcs_list_to_cartesian(coords[index:i]))
                index = i + 1
                break

    segment3 = LineString(Conversions.gcs_list_to_cartesian(coords[index:]))

    for point in points:
        if point.asc_req == -1:
            point = Point(point.longitude, point.latitude)
            print(point.y)
            dist = point.distance(segment1)
            print(point.distance(segment2) / 1000)
            print(point.distance(segment3) / 1000)
            print(dist / 1000)
            breakpoint()




    # if last point < 90 and next point
    #
    # if point in this segment and asc_req == -1:
    #     asc_req =


