import csv
from Point import Point, TypePoint


def read_csv(filename, points_dict):
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
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['rgt', 'trans_type', 'lat', 'lon'])
        for rgt in points_dict:
            for point in points_dict[rgt]:
                writer.writerow([point.rgt, point.state.value, point.latitude, point.longitude])
