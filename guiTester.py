import tkinter as tk
from tkinter import messagebox, filedialog
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
import ShpConverter as Sc

mask_filetype = None  # True represents KML file, False Represents Shp

global root


def get_file():
    global root
    selection_label = tk.Label(root,
                          text='Select a file')
    selection_label.pack(pady=10)
    # file_path = filedialog.askopenfilename(title='Select a file')
    # if file_path:
    #     messagebox.showinfo("File Selected", f"Selected file: {file_path}")
    #     selection_label.pack_forget()
    #     if mask_filetype:
    #         generate_points(file_path)
    #     else:
    #         generate_points(Sc.shp_to_kml(file_path))
    # else:
    #     messagebox.showinfo("No File Selected", "No file was selected")
    #     root.destroy()


def generate_points(mask_file):
    mask_gcs_coords = Kr.parse_mask(mask_file)
    mask_polygons_cart = [Polygon(Conversions.gcs_list_to_cartesian(coords)) for coords in mask_gcs_coords]
    mask_multipolygon = shapely.make_valid(MultiPolygon(mask_polygons_cart))

    off_pointing = None

    def set_mask_pointing(pointing_type):
        nonlocal off_pointing
        off_pointing = pointing_type
        question_label.pack_forget()
        off_button.pack_forget()
        on_button.pack_forget()

    question_label = tk.Label(root,
                          text='Is the input mask an off-pointing region or a RGT region?')
    question_label.pack(pady=10)
    off_button = tk.Button(root, text='Off-Pointing', width=25, command=lambda: set_mask_pointing(False))
    on_button = tk.Button(root, text='RGT', width=25, command=lambda: set_mask_pointing(True))
    off_button.pack()
    on_button.pack()

    land_gcs_coords = Kr.parse_mask('/Users/pvelmuru/Desktop/accurate_land_mask/better/Accurate/land_mask.kml')
    land_polygon_cart = [Polygon(Conversions.gcs_list_to_cartesian(coordinates)) for coordinates in land_gcs_coords]
    land_multipolygon = shapely.make_valid(MultiPolygon(land_polygon_cart))

    new_land_final_multi = None
    if off_pointing:
        new_land_multipolygon = Intersections.combine_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
        new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                         for polygon in new_land_multipolygon.geoms]
        new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))
    else:
        new_land_multipolygon = Intersections.modify_land_mask(land_multipolygon, mask_multipolygon)  # RETURNS back GCS
        new_land_cart = [Polygon(Conversions.gcs_list_to_cartesian(polygon.exterior.coords))
                         for polygon in new_land_multipolygon.geoms]
        new_land_final_multi = shapely.make_valid(MultiPolygon(new_land_cart))


def main():
    global root
    root = tk.Tk()
    root.title("Transition Point Generator")
    root.geometry("550x300")

    question_label = tk.Label(root,
                              text='Is the mask a kml or shapefile?')
    question_label.pack(pady=10)

    def set_mask_filetype(filetype):
        global mask_filetype
        mask_filetype = filetype
        question_label.pack_forget()
        kml_button.pack_forget()
        shp_button.pack_forget()
        print('got here')
        get_file()
        file_path = filedialog.askopenfilename(title='Select a file')

    # file_path = filedialog.askopenfilename(title='Select a file')
    kml_button = tk.Button(root, text='KML', width=25, command=lambda: set_mask_filetype(True))
    shp_button = tk.Button(root, text='Shapefile', width=25, command=lambda: set_mask_filetype(False))
    kml_button.pack(side=tk.LEFT, padx=10, pady=10)
    shp_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()


# rint('Transition Point Modifier')
#
# Is the mask a kml (0) or shapefile (1):
#
# Is the mask an off-pointing mask (0) or shapefile (1):
#
# Enter mask filepath: (Maybe open finder/filer)
#
# Enter initial Transition Point csv file:
#
# Threshold Kilometers?
#
# ....
#
# Generate folder containing:
# 1. csv file with og points
# 2. csv file with ideal points calibration.csv
# 3. Text file with warnings