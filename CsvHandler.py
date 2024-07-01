import csv

import Conversions
from Point import Point, TypePoint


def read_csv(filename, points_dict):
    """
    Reads file and fills up points_dict with Point objects
    :param filename: Csv file names
    :param points_dict: dictionary to fill with Point objects
    :return: populated points_dict
    """
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # Skips headers
        try:
            for row in reader:
                rgt, type_point, latitude, longitude = int(row[0]), int(row[2]), float(row[3]), float(row[4])
                # print(f'rgt:{rgt} point: {type_point} lat: {latitude} long: {longitude}')

                state = TypePoint.RGT if type_point == 0 else TypePoint.VEGETATION

                point = Point(rgt, state, latitude, longitude)
                points_dict[rgt].append(point)
            return points_dict
        except Exception as e:
            print(e)
            print('CSV File format invalid')
            return None


def write_csv(filename, points_dict):
    """

    :param filename: file name to write to
    :param points_dict: dictionary to get information from
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['rgt', 'trans_type', 'lat', 'lon'])
        for rgt in points_dict:
            for point in points_dict[rgt]:
                gcs_coords = Conversions.cartesian_to_gcs(point.latitude, point.longitude)
                writer.writerow([point.rgt, point.state.value, gcs_coords[1], gcs_coords[0]])
