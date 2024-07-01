import Intersections
import KmlReader as Kr
import KmlTester
import Conversions
from shapely import LineString, MultiPolygon, Polygon, MultiLineString, Point
import shapely
import PointerGenerator as Pg
from Segment import Segment, State
import CsvHandler as Ch
import algo
import os


def main():

    mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    # land_gcs_coords = Kr.parse_mask('/Users/pvelmuru/PycharmProjects/Transistion Points/assets/land_mask.kml')
    land_gcs_coords = Kr.parse_mask( '/Users/pvelmuru/Desktop/accurate_land_mask/accurate_land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))
    # new_land_final_multi = shapely.make_valid(new_land_final_multi)

    dir_name = '/Users/pvelmuru/Downloads/IS2_RGTs_cycle12_date_time'
    ext = '.kml'

    file_list = []

    for file in os.listdir(dir_name):
        if file.endswith(ext):
            file_list.append(file)

    file_list.sort()  # Requires consistent file names

    points_dict = {}
    for i in range(1, 1388):
        points_dict[i] = []
    points_dict = Ch.read_csv('/Users/pvelmuru/PycharmProjects/Transistion Points/RGT_transition_locations_V2.0 1.csv',
                              points_dict)

    rgt = 1  # Do not forget the sort -- will sort backwards otherwise
    start_latitude = 0.0279589282518
    start_longitude = -0.131847178124
    for file in file_list:
        orbit_gcs = Kr.get_coordinates_from_kml(dir_name + '/' + file)
        orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
        orbit_line = LineString(orbit_cart)

        # print(list(orbit_line.coords))

        segments = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)

        segments_clean = Pg.merge_touching_segments(segments)
        segments_clean = Pg.remove_insignificant_segments(segments_clean)
        segments_clean = Pg.sort_segments_by_coordinates(segments_clean,
                                                         Conversions.gcs_to_cartesian(start_latitude, start_longitude))
        segments = Pg.remove_segments_under_thresh(segments_clean)
        segments = Pg.merge_rgt_ocean(segments)

        # for segment in segments:
        #     print(segment.state)

        # for point in points_dict[rgt]:
        #     print('point: ', point.longitude, point.latitude)

        Pg.assign_points(rgt, points_dict, segments)

        # TODO ensure coordinates are of right units
        # must happen soon
        # for i in range(len(segments)):
        #     print(i)
        #     print(segments[i].points)

        segments = algo.validate_points(segments)

        points_dict[rgt] = []
        # for segment in segments:  --- does all points, though ideally there is only one per segment
        #     for point in segment.points:
        #         points_dict[rgt].append(point)
        for segment in segments:
            if len(segment.points) != 0:
                points_dict[rgt].append(segment.points[0])

        # test code
        # if rgt == 17:
        #     # print(f'start: {start_latitude}   {start_longitude}')
        #     # test(segments)
        #     print(points_dict[rgt])
        #     return

        # for segment in segments:
        #     if len(segment.points) != 0:
        #         # print(segment.points[0].longitude, segment.points[0].latitude)
        #         print(Conversions.cartesian_to_gcs(segment.points[0].latitude, segment.points[0].longitude))

        rgt += 1
        cart_coords = list(orbit_line.coords)[-1]
        gcs_coords = Conversions.cartesian_to_gcs(cart_coords[1], cart_coords[0])
        start_latitude = gcs_coords[0]
        start_longitude = gcs_coords[1]

    Ch.write_csv('/Users/pvelmuru/Desktop/testwrite.csv', points_dict)


def test(segments):
    mask_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                     for segment in segments if segment.state == State.RGT]

    land_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                     for segment in segments if segment.state == State.VEGETATION]

    ocean_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
                      for segment in segments if segment.state == State.OCEAN]

    # Multi Line String
    if len(mask_segments) != 0:
        print("MASK: ")
        KmlTester.create_file_multiline(MultiLineString(mask_segments))
    if len(land_segments) != 0:
        print("LAND: ")
        KmlTester.create_file_multiline(MultiLineString(land_segments))
    if len(ocean_segments) != 0:
        print("OCEAN: ")
        KmlTester.create_file_multiline(MultiLineString(ocean_segments))


if __name__ == '__main__':
    main()
