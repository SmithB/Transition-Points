import shapely

import Intersections
import KmlReader as Kr
import Conversions
import KmlTester
from shapely import LineString, MultiPolygon, Polygon, MultiLineString
import PointerGenerator as Pg
from Segment import Segment, State
from shapely.ops import transform
from functools import partial
from pyproj import Geod


# TEST SUCCESS
# rgt_coords = KmlReader.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
# # KmlTester.create_file(rgt_coords)
# rgt_cart = Conversions.gcs_list_to_cartesian(rgt_coords)
# # print(rgt_cart)
# rgt_gcs = Conversions.cartesian_list_to_gcs(rgt_cart)
# print(rgt_gcs)
# print(Conversions.cartesian_to_gcs(-2642201.6990687205, -13463.278645213404))
# KmlTester.create_file(rgt_gcs)

#Mask + line intersection test -- Success
# get_line = Intersections.test_get()
# KmlTester.create_file(get_line)
# line_obj = LineString(get_line)
# print(line_obj.length)
#
#
# # DISTANCE CONVERSION CODE
# distance = Conversions.get_geodesic_length(line_obj)
# print(distance)

# Next Test

# TODO find out where this code should go in main
def test_rgt_and_mask_intersection():
    orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
    orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
    orbit_line = LineString(orbit_cart)

    mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    land_gcs_coords = Kr.parse_mask('/Users/pvelmuru/PycharmProjects/Transistion Points//assets/land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    # Added in Intersections
    # intersection = mask_multipolygon.intersection(land_multipolygon)
    # intersection_cart = [Polygon(Conversions.cartesian_list_to_gcs(polygon.exterior.coords)) for polygon in intersection.geoms]
    # intersection_multipolygon = MultiPolygon(intersection_cart)
    # KmlTester.create_file_multipolygon(intersection_multipolygon)
    new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon) # RETURNS back GCS
    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))
    new_land_final_multi = shapely.make_valid(new_land_final_multi)

    # land_rgt_intersec(new_land_final_multi, orbit_line)

    segments = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)

    mask_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                     for segment in segments if segment.state == State.RGT and
                     orbit_line.overlaps(segment.line_string)]

    land_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                     for segment in segments if segment.state == State.VEGETATION and
                     orbit_line.overlaps(segment.line_string)]

    ocean_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                      for segment in segments if segment.state == State.OCEAN and
                      orbit_line.overlaps(segment.line_string)]

    # Multi Line String
    if len(mask_segments) != 0:
        print("MASK: ")
        KmlTester.create_file_multiline(MultiLineString(mask_segments))
    if len(land_segments) != 0:
        print("LAND: ")
        # print(list(land_segments[0].coords))
        KmlTester.create_file_multiline(MultiLineString(land_segments))
    if len(ocean_segments) != 0:
        print("OCEAN: ")
        KmlTester.create_file_multiline(MultiLineString(ocean_segments))


def land_rgt_intersec(land_mask, rgt):
    segments = shapely.make_valid(rgt.intersection(land_mask))
    segments = [shapely.make_valid(LineString(Conversions.cartesian_list_to_gcs(segment.coords))) for segment in segments.geoms if rgt.overlaps(segment)]
    KmlTester.create_file_multiline(shapely.make_valid(MultiLineString(segments)))


test_rgt_and_mask_intersection()

# test_rgt_and_mask_intersection()

# def test_get():
#     # TEST
#     orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
#     # print(orbit_gcs)
#     orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
#     orbit_line = LineString(orbit_cart)
#
#     mask_gcs = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')[1]
#     # print(mask_gcs)
#     mask_cart = Conversions.gcs_list_to_cartesian(mask_gcs)
#     # print(mask_cart)
#     mask_polygon = Polygon(mask_cart)
#
#     land_mask_gcs = Kr.p
#
#     return intersection_list_gcs