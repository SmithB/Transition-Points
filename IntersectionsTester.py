import Intersections
import KmlReader
import Conversions
import KmlTester
from shapely import LineString
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

#NEXT TEST
get_line = Intersections.test_get()
KmlTester.create_file(get_line)
line_obj = LineString(get_line)
print(line_obj.length)


# DISTANCE CONVERSION CODE
distance = Conversions.get_geodesic_length(line_obj)
print(distance)