import Intersections
import KmlReader as Kr
import KmlTester
import Conversions
from shapely import LineString, MultiPolygon, Polygon, MultiLineString
import shapely
import PointerGenerator as Pg
from Segment import State
import CsvHandler as Ch
import algo
import os


def main():
    mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    land_gcs_coords = Kr.parse_mask( '/Users/pvelmuru/Desktop/accurate_land_mask/better/Accurate/land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))

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
        # if rgt == 8:
        #     print(orbit_gcs)
        #     return
        orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
        orbit_line = shapely.make_valid(LineString(orbit_cart))

        segments = Pg.split_ani_meridian(LineString(Conversions.cartesian_list_to_gcs(list(orbit_line.coords))))

        print(f'{rgt} len ', len(segments))

        if len(segments) == 1:
            segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)
            segments_clean = Pg.remove_insignificant_segments(segments_clean)
            segments_clean = Pg.merge_touching_segments(segments_clean)
            segments_clean = Pg.sort_segments_by_coordinates(segments_clean,
                                                             Conversions.gcs_to_cartesian(start_latitude,
                                                                                          start_longitude))
            segments_clean = Pg.remove_segments_under_thresh(segments_clean)
            segments_clean = Pg.merge_rgt_ocean(segments_clean)
            segments_clean = Pg.merge_corresponding_segments(segments_clean)
            segments_clean = Pg.assign_points(rgt, points_dict, segments_clean)

            segments_clean = algo.validate_points(segments_clean, rgt)

            points_dict[rgt] = []
            print(f'rgt: {rgt}: ')
            for segment in segments_clean:
                print(segment.state, segment.length)
                if len(segment.points) != 0:
                    for point in segment.points:
                        points_dict[rgt].append(point)

        else:
            segments_combined = []
            print('Num of segments: ', len(segments))
            for i in range(len(segments)):
                segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi,
                                                 LineString(Conversions.gcs_list_to_cartesian(list(segments[i].coords))))
                segments_clean = Pg.remove_insignificant_segments(segments_clean)
                segments_clean = Pg.merge_touching_segments(segments_clean)
                segments_clean = Pg.sort_segments_by_coordinates(segments_clean,
                                                                 Conversions.gcs_to_cartesian(start_latitude,
                                                                                              start_longitude))
                segments_clean = Pg.remove_segments_under_thresh(segments_clean)
                segments_clean = Pg.merge_rgt_ocean(segments_clean)

                segments_combined.extend(segments_clean)

                coordinates = Conversions.cartesian_to_gcs(list(segments_combined[-1].line_string.coords)[-1][0],
                                                           list(segments_combined[-1].line_string.coords)[-1][1])
                start_longitude = - coordinates[0]
                start_latitude = coordinates[1]
                print('num_split: ', len(segments_clean))
                print([segment.state for segment in segments_clean])
                print('lats: ', start_longitude, start_latitude)

            segments_combined = Pg.merge_corresponding_segments(segments_combined)
            segments_combined = Pg.assign_points(rgt, points_dict, segments_combined)

            segments_combined = algo.validate_points(segments_combined, rgt)

            points_dict[rgt] = []
            print(f'rgt: {rgt}: ')
            for segment in segments_combined:
                print(segment.state, segment.length)
                if len(segment.points) != 0:
                    for point in segment.points:
                        points_dict[rgt].append(point)
                        # if rgt == 8:
                        #     longitude, latitiude = Conversions.cartesian_to_gcs(point.longitude, point.latitude)
                        #     if longitude == 8.983152841195214e-06:
                        #         print(Conversions.cartesian_list_to_gcs(list(segment.line_string.coords)))
                        #     print(Conversions.cartesian_to_gcs(point.longitude, point.latitude), point.endpoint)

        rgt += 1
        cart_coords = orbit_gcs[-1]
        print(cart_coords)
        gcs_coords = cart_coords[0], cart_coords[1]
        start_longitude = gcs_coords[0]
        start_latitude = gcs_coords[1]
        print(f'rgt {rgt}: last coords: {start_latitude} {start_longitude}')

    Pg.remove_twilight_points(points_dict)
    Pg.remove_duplicate_points(points_dict)
    Pg.remove_extra_endpoints(points_dict)

    Ch.write_csv('/Users/pvelmuru/Desktop/testwrite.csv', points_dict)

    transition_errors = Pg.generate_transition_errors(points_dict)
    singular_point_errors = Pg.singular_point_errors(points_dict)
    print_transition_errors(transition_errors)
    print_transition_errors(singular_point_errors)
    print(f'Num cross: {len(Pg.crossing_rgts)}')
    print(Pg.crossing_rgts)


def print_transition_errors(transition_errors):
    print('Potential Transition Errors')
    for rgt in transition_errors:
        print(f'Rgt: {rgt}')

    print(f'Num errors: {len(transition_errors)}')


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
