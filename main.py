import Intersections
import KmlReader as Kr
import Conversions
from shapely import LineString, MultiPolygon, Polygon
import shapely
import algo
import ShpConverter
import CsvHandler as Ch
import AscReq
import os
import traceback
import Warnings
import gui
import shutil


def main():

    gui.run()
    kml = True if gui.mask_filetype == 'KML' else False
    off_pointing = True if gui.mask_region_type == 'Off-Pointing' else False
    mask_filepath = gui.mask_filepath
    transition_csv_path = gui.transition_csv_path
    threshold_kilometers = gui.threshold_kilometers

    # off_pointing = False

    if off_pointing:
        import CombinePointGenerator as Pg
    else:
        import PointerGenerator as Pg

    Pg.MIN_TRANSITION_DIST = threshold_kilometers

    # kml = False

    if kml:
        # mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
        mask_gcs_coords = Kr.parse_mask(mask_filepath)
    else:
        try:
            # mask_gcs_coords = Kr.parse_mask(ShpConverter.shp_to_kml('/Users/pvelmuru/Downloads/AntarcticaGreenland'))
            mask_gcs_coords = Kr.parse_mask(ShpConverter.shp_to_kml(mask_filepath))
        except:
            traceback.print_exc()


    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    # land_gcs_coords = Kr.parse_mask( '/Users/pvelmuru/Desktop/accurate_land_mask/better/Accurate/land_mask.kml')
    land_gcs_coords = Kr.parse_mask(os.path.join('assets', 'land_mask.kml'))
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    if not off_pointing:
        new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
    else:
        new_land_multipolygon = Intersections.combine_land_mask(land_multipolygon, mask_multipolygon)

    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))

    dir_name = os.path.join('assets', 'IS2_RGTs_cycle12_date_time')
    ext = '.kml'

    file_list = []

    for file in os.listdir(dir_name):
        if file.endswith(ext):
            file_list.append(file)

    file_list.sort()  # Requires consistent file names

    points_dict = {}
    for i in range(1, 1388):
        points_dict[i] = []
    # points_dict = Ch.read_csv('/Users/pvelmuru/PycharmProjects/Transistion Points/RGT_transition_locations_V2.0 1.csv',
    #                           points_dict)

    points_dict = Ch.read_csv(transition_csv_path, points_dict)

    rgt = 1
    start_latitude = 0.0279589282518
    start_longitude = -0.131847178124
    for file in file_list:
        orbit_gcs = Kr.get_coordinates_from_kml(os.path.join(dir_name, file))
        orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
        orbit_line = shapely.make_valid(LineString(orbit_cart))

        segments = Pg.split_ani_meridian(LineString(Conversions.cartesian_list_to_gcs(list(orbit_line.coords))))

        print(f'rgt {rgt} len ', len(segments))

        if len(segments) == 1:
            if off_pointing:
                segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)
            else:
                segments_clean = Pg.segmentation(new_land_final_multi, orbit_line)
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
            for i in range(len(segments)):
                if not off_pointing:
                    segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi,
                                                     LineString(
                                                         Conversions.gcs_list_to_cartesian(list(segments[i].coords))))
                else:
                    segments_clean = Pg.segmentation(new_land_final_multi,
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

            segments_combined = Pg.merge_corresponding_segments(segments_combined)
            print('Num Segments: ', len(segments_combined))
            print([(segment.state, segment.length) for segment in segments_combined])
            segments_combined = Pg.assign_points(rgt, points_dict, segments_combined)
            # print([segment.points for segment in segments_combined])

            segments_combined = algo.validate_points(segments_combined, rgt)

            print([(i, point.state) for i, segment in enumerate(segments_combined) for point in segment.points])
            points_dict[rgt] = []
            print(f'rgt: {rgt}: ')
            for segment in segments_combined:
                # print(segment.state, segment.length)
                if len(segment.points) != 0:
                    for point in segment.points:
                        points_dict[rgt].append(point)

            AscReq.generate_asc_req(orbit_gcs, points_dict[rgt])

        rgt += 1
        cart_coords = orbit_gcs[-1]
        gcs_coords = cart_coords[0], cart_coords[1]
        start_longitude = gcs_coords[0]
        start_latitude = gcs_coords[1]

    Pg.remove_twilight_points(points_dict)
    Pg.remove_duplicate_points(points_dict)
    Pg.remove_extra_endpoints(points_dict)
    Pg.remove_points_under_threshold(points_dict, Pg.MIN_TRANSITION_DIST)

    # Ch.write_csv('/Users/pvelmuru/Desktop/testwrite.csv', points_dict)
    Ch.write_csv(os.path.join('assets', 'new_points.csv'), points_dict)

    transition_errors = Pg.generate_transition_errors(points_dict)
    # singular_point_errors = Pg.singular_point_errors(points_dict)
    Warnings.generate_warnings(transition_errors, Pg.significant_rgts_under_thresh, points_dict, Pg.MIN_TRANSITION_DIST)

    source_directory = os.path.join(os.getcwd(), "assets")
    files = ['new_points.csv', 'warnings.txt']
    for filename in files:
        source_path = os.path.join(source_directory, filename)
        destination_path = os.path.join(gui.files_destination, filename)
        shutil.copy(source_path, destination_path)
    # print_transition_errors(transition_errors)
    # print_transition_errors(singular_point_errors)
    # print(f'Num cross: {len(Pg.crossing_rgts)}')
    # print(Pg.crossing_rgts)


# def print_transition_errors(transition_errors):
#     print('Potential Transition Errors')
#     for rgt in transition_errors:
#         print(f'Rgt: {rgt}')
#
#     print(f'Num errors: {len(transition_errors)}')
#
#
# def test(segments):
#     mask_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
#                      for segment in segments if segment.state == State.RGT]
#
#     land_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
#                      for segment in segments if segment.state == State.VEGETATION]
#
#     ocean_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
#                       for segment in segments if segment.state == State.OCEAN]
#
#     # Multi Line String
#     if len(mask_segments) != 0:
#         print("MASK: ")
#         KmlTester.create_file_multiline(MultiLineString(mask_segments))
#     if len(land_segments) != 0:
#         print("LAND: ")
#         KmlTester.create_file_multiline(MultiLineString(land_segments))
#     if len(ocean_segments) != 0:
#         print("OCEAN: ")
#         KmlTester.create_file_multiline(MultiLineString(ocean_segments))


if __name__ == '__main__':
    main()
