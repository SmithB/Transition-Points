import Intersections
import KmlReader as Kr
import Conversions
import KmlTester
from shapely import LineString, MultiPolygon, Polygon, MultiLineString, Point
import shapely
import PointerGenerator as Pg
from Segment import Segment, State
import CsvHandler as Ch


# TODO find out where this code should go in main
def test_rgt_and_mask_intersection():
    # orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Desktop/IS2_RGT_0001_cycle12_23-Jun-2021.kml')
    orbit_gcs = Kr.get_coordinates_from_kml('/Users/pvelmuru/Downloads/IS2_RGTs_cycle12_date_time/IS2_RGT_0017_cycle12_24-Jun-2021.kml')
    orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
    orbit_line = LineString(orbit_cart)

    mask_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/snow_depth_mask.kml')
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    land_gcs_coords = Kr.parse_mask('/Users/pvelmuru/PycharmProjects/Transistion Points/assets/land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    # Added in Intersections
    new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))
    new_land_final_multi = shapely.make_valid(new_land_final_multi)

    segments = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)
    # Leave as Segment objects when doing actually, needs length stuff
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

    segments_clean = Pg.merge_touching_segments(segments)
    segments_clean = Pg.remove_insignificant_segments(segments_clean)
    segments_clean = Pg.remove_segments_under_thresh(segments_clean)
    segments_clean = Pg.sort_segments_by_coordinates(segments_clean,  Conversions.gcs_to_cartesian(0.021, -18.04))
    print("new")
    for segment in segments_clean:
        print(f'{segment.state}: {segment.length}')
    print(len(segments_clean))
    Pg.generate_ideal_points(segments_clean)

    points_dict = {}
    for i in range(1, 1388):
        points_dict[i] = []

    points_dict = Ch.read_csv('/Users/pvelmuru/PycharmProjects/Transistion Points/RGT_transition_locations_V2.0 1.csv',
                              points_dict)
    Pg.assign_points(17, points_dict, segments_clean)


    # ocean_segments = [LineString(Conversions.cartesian_list_to_gcs(segment.line_string.coords))
    #                   for segment in segments_clean if segment.state == State.OCEAN]
    # print("OCEAN CLEAN: ")
    # KmlTester.create_file_multiline(MultiLineString(ocean_segments))


test_rgt_and_mask_intersection()
