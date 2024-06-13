from fastkml import kml
from pygeoif import LineString, Polygon, MultiPolygon
# from shapely.geometry import LineString, Polygon


def get_coordinates_from_kml(file):
    with open(file, 'rt') as file:
        doc = file.read()
        print(doc)
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
            coordinates = parse_placemark(placemark, coordinates)
        elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
            coordinates = parse_features(feature.features(), coordinates)
    return coordinates


def parse_placemark(placemark, coordinates):
    print(type(placemark.geometry))
    if isinstance(placemark.geometry, LineString):
        coordinates.extend(placemark.geometry.coords)
    elif isinstance(placemark.geometry, Polygon):
        coordinates.extend(placemark.geometry.exterior.coords)
    # elif isinstance(placemark.geometry, MultiPolygon):
    #     coordinates.extend(placemark.geometry.)
    return coordinates


def parse_mask_polygons(document, mask_polygons):
    for feature in document:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            mask_polygons = parse_mask_features(placemark, mask_polygons)
        elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
            mask_polygons = parse_mask_polygons(feature.features(), mask_polygons)
    return mask_polygons


def parse_mask_features(placemark, mask_polygons):
    print(type(placemark.geometry))
    if isinstance(placemark.geometry, MultiPolygon):
        print("here")
        multi_polygon = placemark.geometry
        # print(multi_polygon.geoms[0])
        for polygon in multi_polygon.geoms:
            print(type(polygon))
            if isinstance(polygon, Polygon):
                mask_polygons.append(polygon)
    elif isinstance(placemark.geometry, Polygon):
        mask_polygons.append(placemark.geometry)
    return mask_polygons

# parse_mask to parse_mask_polygon to parse_mask_polygons


def parse_mask(file):
    with open(file, 'rt') as file:
        doc = file.read()
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))

        mask_polygons = []
        document = list(k.features())
        mask_polygons = parse_mask_polygons(document, mask_polygons)
        # mask_polygons[0].exterior.coords
        return mask_polygons


print(get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml'))
# print(get_coordinates_from_kml('/Users/pvelmuru/Desktop/snow_depth_mask.kml'))
# print(get_coordinates_from_kml('/Users/pvelmuru/Downloads/Placemark.kml'))
# print(get_coordinates_from_kml('/Users/pvelmuru/Downloads/Polygon.kml'))
# print(parse_mask('/Users/pvelmuru/Downloads/Polygon.kml'))
print(parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml'))
print("yay")
