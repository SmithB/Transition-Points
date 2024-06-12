from fastkml import kml
from pygeoif import LineString, Polygon
# from shapely.geometry import LineString, Polygon


def get_coordinates_from_kml(file):
    with open(file, 'rt') as file:
        doc = file.read()
        print(doc)
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))

        coordinates = []
        document = list(k.features())
        parse_features(document, coordinates)

        return coordinates


def parse_features(document, coordinates):
    for feature in document:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            print("HEEERE: ", placemark)
            coordinates = parse_geometries(placemark, coordinates)
        elif isinstance(feature, kml.Folder):
            print("FOLDER")
            coordinates = parse_placemarks(list(feature.features()), coordinates)
        elif isinstance(feature, kml.Document):
            print("DOCUMENT")
            coordinates = parse_features(feature.features(), coordinates)
    return coordinates


def parse_placemarks(features, coordinates):
    for feature in features:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            coordinates = parse_geometries(placemark, coordinates)
    return coordinates


def parse_geometries(placemark, coordinates):
    print("got here")
    print(type(placemark.geometry))
    print(isinstance(placemark.geometry, LineString))
    if isinstance(placemark.geometry, LineString):
        print("hpm")
        coordinates.extend(placemark.geometry.coords)
    elif isinstance(placemark.geometry, Polygon):
        print("poly?")
        coordinates.extend(placemark.geometry.exterior.coords)
    return coordinates


print(get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml'))
print("yay")
