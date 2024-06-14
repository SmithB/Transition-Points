from shapely import LineString, Polygon
import Conversions # Only for testing
import KmlReader as Kr

#  Maybe use union to convert the mask multipolygon into a singular polygon


def find_intersections(geometry1, geometry2):
    print("Issue ", geometry2)
    print(geometry1)
    intersection = geometry1.intersection(geometry2)
    return list(intersection.coords)

# TODO


def modify_ocean_mask(ocean_mask, rgt_mask):
    intersection = find_intersections(ocean_mask, rgt_mask)

# TEST
orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
print(orbit_gcs)
orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
orbit_line = LineString(orbit_cart)

mask_gcs = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')[1]
print(mask_gcs)
mask_cart = Conversions.gcs_list_to_cartesian(mask_gcs)
print(mask_cart)
mask_polygon = Polygon(mask_cart)


print(orbit_line)


intersection_list = find_intersections(orbit_line, mask_polygon)

intersection_list_gcs = Conversions.cartesian_list_to_gcs(intersection_list)
print(intersection_list_gcs)

# a = LineString([(0, 0), (1, 1), (1,2), (2,2)])
# b = LineString([(0, 0), (1, 1), (2,1), (2,2)])
# x = a.intersection(b)
#
# print(x)
# print(find_intersections(a, b))
