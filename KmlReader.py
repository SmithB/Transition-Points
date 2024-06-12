from fastkml import kml
from pygeoif import LineString, Polygon
# from shapely.geometry import LineString, Polygon


def get_coordinates_from_kml(file):
    with open(file, 'rt') as file:
        doc = file.read()
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))

        coordinates = []
        document = list(k.features())
        coordinates = parse_features(document, coordinates)

        return coordinates


def parse_features(document, coordinates):
    for feature in document:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            coordinates = parse_geometries(placemark, coordinates)
        elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
            coordinates = parse_features(feature.features(), coordinates)
    return coordinates


def parse_geometries(placemark, coordinates):
    # print(type(placemark.geometry))
    if isinstance(placemark.geometry, LineString):
        coordinates.extend(placemark.geometry.coords)
    elif isinstance(placemark.geometry, Polygon):
        coordinates.extend(placemark.geometry.exterior.coords)
    return coordinates


print(get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml'))
print("yay")
