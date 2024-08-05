"""
Module extracts geometries from kml a file
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""

from fastkml import kml
from pygeoif import LineString, Polygon, MultiPolygon


def get_coordinates_from_kml(file):
    """
    Gets GCS coordinates of a LineString from a kml file
    :param file: kml filename
    :return: coordinates for a LineString
    """
    with open(file, 'rt') as file:
        doc = file.read()
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))

        coordinates = []
        document = list(k.features())
        coordinates = parse_features(document, coordinates)

        return coordinates


def parse_features(document, coordinates):
    """
    Helper function that parses a kml document to extract the coordinates
    :param document: Current document to parse
    :param coordinates: list of coordinates
    :return: coordinates for a LineString
    """
    for feature in document:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            coordinates = parse_placemark(placemark, coordinates)
        elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
            coordinates = parse_features(feature.features(), coordinates)
    return coordinates


def parse_placemark(placemark, coordinates):
    """
    Helper function that adds coordinates it finds to the coordinates list
    :param placemark: Current kml feature
    :param coordinates: list of coordinates
    :return: list of modified coordinates
    """
    if isinstance(placemark.geometry, LineString):
        coordinates.extend(placemark.geometry.coords)
    elif isinstance(placemark.geometry, Polygon):
        coordinates.extend(placemark.geometry.exterior.coords)
    return coordinates


def parse_mask_polygons(document, mask_polygons):
    """
    Helper function that parses the given document for features in kml file
    :param document: Current section to parse
    :param mask_polygons: a list of lists of coordinates for polygons
    :return:  a list of lists of coordinates for polygons
    """
    for feature in document:
        if isinstance(feature, kml.Placemark):
            placemark = feature
            mask_polygons = parse_mask_features(placemark, mask_polygons)
        elif isinstance(feature, kml.Folder) or isinstance(feature, kml.Document):
            mask_polygons = parse_mask_polygons(feature.features(), mask_polygons)
    return mask_polygons


def parse_mask_features(placemark, mask_polygons):
    """
    Helper function that parses features for polygons and multipolygons
    :param placemark: Current feature to parse
    :param mask_polygons:  a list of lists of coordinates for polygons
    :return:  a list of lists of coordinates for polygons
    """
    if isinstance(placemark.geometry, MultiPolygon):
        multi_polygon = placemark.geometry
        for polygon in multi_polygon.geoms:
            if isinstance(polygon, Polygon):
                mask_polygons.append(polygon.exterior.coords)
    elif isinstance(placemark.geometry, Polygon):
        mask_polygons.append(placemark.geometry.exterior.coords)
    return mask_polygons


def parse_mask(file):
    """
    Function get the coordinates for multipolygons or polygons from a kml file

    :param file: kml filename
    :return: a list of lists of coordinates for polygons
    """
    with open(file, 'rt') as file:
        doc = file.read()
        k = kml.KML()
        k.from_string(doc.encode('utf-8'))

        mask_polygons = []
        document = list(k.features())
        mask_polygons = parse_mask_polygons(document, mask_polygons)
        return mask_polygons
