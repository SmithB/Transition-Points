import Intersections
import KmlReader as Kr
import Conversions
import KmlTester
from shapely import LineString, MultiPolygon, Polygon, MultiLineString
import shapely
import PointerGenerator as Pg
from Segment import Segment, State


# Next Test

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
    new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon) # RETURNS back GCS
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
                      for segment in segments if segment.state == State.OCEAN and
                      segment.line_string.dwithin(orbit_line, 1e-8)]

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
    print(len(mask_segments))
    print(Conversions.get_geodesic_length(mask_segments[0]))
    print(land_segments[1].length)
    print(mask_segments[0].length)
    print(len(land_segments))
    print(len(ocean_segments))
    print(len(segments))


test_rgt_and_mask_intersection()
