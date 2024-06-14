from shapely import LineString, Polygon
import Conversions # Only for testing
import KmlReader as Kr

#  Maybe use union to convert the mask multipolygon into a singular polygon


def find_intersections(geometry1, geometry2):
    # print("Issue ", geometry2)
    # print(geometry1)
    intersection = geometry1.intersection(geometry2)
    # print("Intersection: ", intersection)
    return intersection

# TODO


def modify_ocean_mask(ocean_mask, rgt_mask):
    intersection = find_intersections(ocean_mask, rgt_mask)

# TEST
orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
# print(orbit_gcs)
orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
orbit_line = LineString(orbit_cart)

mask_gcs = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')[1]
# print(mask_gcs)
mask_cart = Conversions.gcs_list_to_cartesian(mask_gcs)
# print(mask_cart)
mask_polygon = Polygon(mask_cart)


# print(orbit_line)

def test_get():
    intersection = find_intersections(orbit_line, mask_polygon)
    # print(list(intersection.geoms))

    intersection_list_gcs = Conversions.cartesian_list_to_gcs(intersection.geoms[1].coords)
    # print(intersection.geoms[0])
    print("COORDS: ", intersection.geoms[1].coords[0])
    print(type(intersection.geoms[1]))
    print("OTHER: ", intersection_list_gcs[0])
    return intersection_list_gcs
    # return intersection_list_gcs[0]

# a = LineString([(20037508.342789244, 12271583.545960385), (19784630.342199467, 12193126.476137), (1,2), (2,2)])
# b = LineString([(0, 0), (1, 1), (2,1), (2,2)])
# x = a.intersection(mask_polygon)
#
# print(x)
# print(find_intersections(a, b))
