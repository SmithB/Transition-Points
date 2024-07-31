import Conversions
from shapely import LineString, Point


def generate_warnings(transition_errors, significant_rgts_under_thresh, points_dict, threshold):
    too_close_rgts = check_too_close_points(points_dict)
    rgts_within_thresh = points_within_threshold(points_dict, threshold)
    with open('assets/warnings.txt', 'w') as file:
        file.write('Errors:\n')
        for error in transition_errors:
            file.write(f'RGT: {error} \n')

        file.write('Distance Errors:\n')
        for rgt in rgts_within_thresh:
            file.write(f'RGT: {rgt}\n')
        file.write("\n\n")

        file.write('Warnings:\n')
        file.write('RGTs where large segments under threshold were skipped:\n')
        for rgt in significant_rgts_under_thresh:
            file.write(f'RGT: {rgt}\n')

        file.write('RGTs where there are multiple Transition Points in a 1500 km distance:\n')
        for rgt in too_close_rgts:
            file.write(f'RGT: {rgt}\n')
        file.write('\nGood Luck!')


def check_too_close_points(points_dict):
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
                too_close_rgts.append(f'{rgt}  {i}')

    return too_close_rgts


def points_within_threshold(points_dict, threshold):
    rgts = []

    for rgt in range(1, 1388):
        for i in range(len(points_dict[rgt]) - 1):
            points = points_dict[rgt]
            point1 = Point(Conversions.cartesian_to_gcs(points[i].longitude, points[i].latitude))
            point2 = Point(Conversions.cartesian_to_gcs(points[i + 1].longitude, points[i + 1].latitude))
            line = LineString([point1, point2])
            length = Conversions.get_geodesic_length(line)

            if length < threshold:
                rgts.append(f'{rgt}  {i}')

    return rgts
