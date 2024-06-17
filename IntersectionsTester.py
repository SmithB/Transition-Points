import Intersections
import KmlReader as Kr
import Conversions
import KmlTester
from shapely import LineString, MultiPolygon, Polygon
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
def test_rgt_and_mask_intersection():
    mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = MultiPolygon(mask_polygons_cart)

    land_gcs_coords = Kr.parse_mask('/Users/pvelmuru/PycharmProjects/Transistion Points/assets/land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = MultiPolygon(land_polygon_cart)
    intersection = mask_multipolygon.intersection(land_multipolygon)
    intersection_cart = [Polygon(Conversions.cartesian_list_to_gcs(polygon.exterior.coords)) for polygon in intersection.geoms]
    intersection_multipolygon = MultiPolygon(intersection_cart)
    KmlTester.create_file_multipolygon(intersection_multipolygon)

test_rgt_and_mask_intersection()
