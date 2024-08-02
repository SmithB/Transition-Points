import os
import traceback

from tqdm import tqdm
from shapely import LineString, MultiPolygon, Polygon
import shapely

import Intersections
import KmlReader as Kr
import Conversions
import algo
import ShpConverter
import FileManager as Fm
import AscReq
import Warnings
import gui

"""
This script processes Transition Points and a mask to generate new Transition Points based on user inputs from a GUI.
Supports handling both KML and Shapefile masks. Script uses the RGTs from Cycle 12 to create, delete, and modify the
Transition Points. The RGTs are segmented and assigned transition points based off user-input mask, Land Mask, and other
thresholds. The final points are then validated, filtered, and written to a csv file. Script also generates warnings for
transition errors and downloads final files to a desired destination.

Modules:
    Intersections: Contains functions for modifying and combining land masks
    KmlReader (Kr): Reads and parses KML files
    Conversions: Converts coordinates between geographic coordinate systems (GCS) and Cartesian
    shapely: Library used for manipulation and analysis of planar geometries
    algo: Processes and validating segments and Transition Points
    ShpConverter: Converts Shapefiles to KML format
    FileManager (Fm): Manages file read/write operations (csv and txt)
    AscReq: Generates asc_reqs
    Warnings: Generates warnings for RGTs that could use human supervision
    gui: Handles user inputs required for computations
    tqdm: Produces a progress bar for tracking the processing of files

Author:
    Pranesh Velmurugan praneshsvels@gmail.com
"""


def main():
    """
    Function orchestrates the entire processing pipeline.

    Steps:
        1. Gather user inputs with gui
        2. Processes mask file (KML or Shapefile)
        3. Generate new land mask by combining or modifying the existing one
        4. Read and processes the RGTs from Cycle 12
        5. Generates segments and assigns points
        6. Validate and filter points
        7. Writes final points to a CSV file
        8. Generates transition errors and warnings
        9. Downloads final files to specified destination
    """

    gui.run()

    # Sets vars based off user inputs
    kml = True if gui.mask_filetype == 'KML' else False
    off_pointing = True if gui.mask_region_type == 'Off-Pointing' else False
    mask_filepath = gui.mask_filepath
    transition_csv_path = gui.transition_csv_path
    threshold_kilometers = gui.threshold_kilometers

    # Conditional import based on type of mask
    if off_pointing:
        import CombinePointGenerator as Pg
    else:
        import PointerGenerator as Pg

    Pg.MIN_TRANSITION_DIST = threshold_kilometers

    # Converts mask to kml if necessary
    if kml:
        mask_gcs_coords = Kr.parse_mask(mask_filepath)
    else:
        try:
            mask_gcs_coords = Kr.parse_mask(ShpConverter.shp_to_kml(mask_filepath))
        except:
            traceback.print_exc()

    # Converts coordinates to cartesian to prepare for shapely processing
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    land_gcs_coords = Kr.parse_mask(os.path.join('assets', 'land_mask.kml'))
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    # Combines mask and land mask or modifies land mask based on type of pointing required
    if not off_pointing:
        new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
    else:
        new_land_multipolygon = Intersections.combine_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS

    # Validates the new land mask
    new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                     for polygon in new_land_multipolygon.geoms]
    new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))

    # Creates a list of all the RGT files
    dir_name = os.path.join('assets', 'IS2_RGTs_cycle12_date_time')
    ext = '.kml'

    file_list = []

    for file in os.listdir(dir_name):
        if file.endswith(ext):
            file_list.append(file)

    file_list.sort()  # Requires consistent file names

    # Initalizes and populates a dictionary containing all the original Transition Points for each RGT
    points_dict = {}
    for i in range(1, 1388):
        points_dict[i] = []
    points_dict = Fm.read_csv(transition_csv_path, points_dict)

    # Processes all 1387 RGTs, segments them, and modifies Transition Points
    rgt = 1
    start_latitude = 0.0279589282518  # Required for sorting
    start_longitude = -0.131847178124  # Required for sorting
    pbar = tqdm(total=1387, desc='Processing', colour='blue')  # Initializes console status bar

    for file in file_list:
        # Reads RGT coordinates from file and converts that into a cartesian LineString
        orbit_gcs = Kr.get_coordinates_from_kml(os.path.join(dir_name, file))
        orbit_cart = Conversions.gcs_list_to_cartesian(orbit_gcs)
        orbit_line = shapely.make_valid(LineString(orbit_cart))

        # Splits RGT into segments if portions cross the anti meridian
        segments = Pg.split_anti_meridian(LineString(Conversions.cartesian_list_to_gcs(list(orbit_line.coords))))

        if len(segments) == 1:  # This means that the RGT did not cross the antimeridian
            if off_pointing:
                segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi, orbit_line)
            else:
                segments_clean = Pg.segmentation(new_land_final_multi, orbit_line)

            # Cleans segments and assigns points to them
            segments_clean = Pg.remove_insignificant_segments(segments_clean)
            segments_clean = Pg.merge_touching_segments(segments_clean)
            segments_clean = Pg.sort_segments_by_coordinates(segments_clean,
                                                             Conversions.gcs_to_cartesian(start_latitude,
                                                                                          start_longitude))
            segments_clean = Pg.remove_segments_under_thresh(segments_clean)
            segments_clean = Pg.merge_rgt_ocean(segments_clean)
            segments_clean = Pg.merge_corresponding_segments(segments_clean)
            segments_clean = Pg.assign_points(rgt, points_dict, segments_clean)

            segments_clean = algo.validate_points(segments_clean, rgt)  # Validates the points

            # Stores the points in the points_dict dictionary
            points_dict[rgt] = []
            for segment in segments_clean:
                if len(segment.points) != 0:
                    for point in segment.points:
                        points_dict[rgt].append(point)

        else:
            segments_combined = []  # list of all segments
            for i in range(len(segments)):
                if not off_pointing:
                    segments_clean = Pg.segmentation(mask_multipolygon, new_land_final_multi,
                                                     LineString(
                                                         Conversions.gcs_list_to_cartesian(list(segments[i].coords))))
                else:
                    segments_clean = Pg.segmentation(new_land_final_multi,
                                                     LineString(Conversions.gcs_list_to_cartesian(list(segments[i].coords))))

                # Cleans segments and assigns points to them
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

            # Merges segments split by antimeridian
            segments_combined = Pg.merge_corresponding_segments(segments_combined)
            segments_combined = Pg.assign_points(rgt, points_dict, segments_combined)

            segments_combined = algo.validate_points(segments_combined, rgt)  # Validates the points

            # Stores the points in the points_dict dictionary
            points_dict[rgt] = []
            for segment in segments_combined:
                if len(segment.points) != 0:
                    for point in segment.points:
                        points_dict[rgt].append(point)

        # Generates Ascending Requirements
        AscReq.generate_asc_req(orbit_gcs, points_dict[rgt])  # TODO I moved, double check it works

        rgt += 1
        cart_coords = orbit_gcs[-1]
        gcs_coords = cart_coords[0], cart_coords[1]
        start_longitude = gcs_coords[0]
        start_latitude = gcs_coords[1]
        pbar.update(1)

    # Filters out points that are unnecessary
    Pg.remove_twilight_points(points_dict)
    Pg.remove_duplicate_points(points_dict)
    Pg.remove_extra_endpoints(points_dict)
    Pg.remove_points_under_threshold(points_dict, Pg.MIN_TRANSITION_DIST)

    Fm.write_csv(os.path.join('assets', 'new_points.csv'), points_dict)

    transition_errors = Pg.generate_transition_errors(points_dict)
    Warnings.generate_warnings(transition_errors, Pg.significant_rgts_under_thresh, points_dict, Pg.MIN_TRANSITION_DIST)

    Fm.download_files(gui.files_destination)


if __name__ == '__main__':
    main()
