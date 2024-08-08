# Software Description:

This script processes existing Transition Points and a mask to generate a new set of Transition Points based on user inputs from a GUI. Supports handling both KML and Shapefile masks. Script uses the KML files from ICESat-2 Cycle 12 (RGT-pointing only) to create, delete, and modify the Transition Points. The RGTs are segmented and assigned transition points based off user-input mask, Land Mask, and other thresholds. The final points are then validated, filtered, and written to a csv file. Script also generates warnings for transition errors and downloads final files to a desired destination. Note “RGTs” and “KML files” are used interchangeably in this document.

# How to run Program:
## 1. Download Required Libraries:
In a terminal window
Try:
`pip install -r requirements.txt`

If that fails try:
`pip install shapely==2.0.4 pyproj==3.6.1 fastkml==0.12 geopandas==1.0.0 fiona==1.9.6 lxml==5.2.2 tdqm==0.0.1`
May have to uninstall older versions of these libraries if they are already present

## 2. Run the main script to start the program:
Navigate to the Transition-Points-main directory and run
python main.py
Wait for the GUI to pop up

## 3. Follow the Instructions from the GUI:
Input the necessary files and fields.

# Modules:
### Main: 
Function orchestrates the entire processing pipeline.

    Steps:
        1. Gather user inputs with GUI
        2. Processes mask file (KML or Shapefile)
        3. Generate new land mask by combining or modifying the existing one
        4. Read and processes the RGTs (KML files) from Cycle 12
        5. Generates segments and assigns points
        6. Validate and filter points
        7. Write final points to a CSV file
        8. Generate transition errors and warnings
        9. Download final files to specified destination

### algo: 
Processes and validates segments and Transition Points. The transition points get modified, deleted, and created here.

### AscReq: 
Has a function to generate ascending requirements.

### CombinePointGenerator and PointGenerator:
Contains functions to segment RGTs based on mask and land mask intersections. It also cleans up the intersections (fixes floating-point precision errors) and removes extra transition points that were generated. CombinePointGenerator is used for Off-pointing masks and PointGenerator is used for RGT masks. The main difference is that the initial segmentation is done differently between the two. 

### Conversions: 
Converts coordinates between geographic coordinate systems (GCS) and Cartesian units. Also finds the geodesic length of a line segment.

### FileManager: 
Manages file read/write operations (csv and txt). Also downloads generated files to the specified directory.

### gui: 
Creates a Graphical User Interfaces and handles user inputs required for computations.

### Intersections: 
Contains functions for modifying and combining land masks. Also, finds intersections between geometries.

### KmlReader: 
Reads and parses KML files.

### KmlTester:
Module not used actively in code. Used when debugging generated geometries. It can print geometries in kml format. The printed-out text can be put in a kml file and then can be loaded into Google Earth to verify the geometry.

### Point:
This class allows the creation of a point. A Point contains these attributes: rgt number, state (RGT or Veg/Off), latitude, longitude, asc_req, endpoint (Whether or not the point is an endpoint of a segment), created (Whether or not the point was created by the program).

### Segment:
This class allows the creation of a segment. A Segment contains these attributes: LineString, state (RGT, Veg/Off, Ocean), length, points.

### ShpConverter: 
Converts Shapefiles to kml files.
   
### Warnings: 
Generates warnings for RGTs that could use human supervision. Warnings include situations where a segment was skipped because ICESat-2 could not make the transition due to segment length, but the segment is still noticeably big. Writes errors and warnings to warnings.txt. Warnings generally indicate where code skips a segment where a potential transition point might be made for the reasons listed above.

Types of errors/warnings:
•	Error: When an RGT just didn’t work and needs to be done by hand
•	Warning 1: “length warning”: IS2 physically can’t make a transition point at a particular location (NOT the whole RGT) – specific location needs to be done by hand if desired
•	Warning 2 “3 transition points within 1500 km”: Generates the new transition points; assumes 550 km limitation on IS2 transition modes is accurate. If threshold is set above 750 km, this warning shouldn’t show up at all.
# External Libraries Used: 

Shapely (Geometric Objects Manipulation) - https://shapely.readthedocs.io/en/stable/index.html 

Pyproj (Units Conversion Library) - https://pyproj4.github.io/pyproj/stable/ 

FastKML (kml File Parsing Library) - https://fastkml.readthedocs.io/en/latest/usage_guide.html 

GeoPandas (Geospatial Data Operations) – https://geopandas.org/en/stable/index.html 

Tdqm (Progress Status Bar) - https://tqdm.github.io 
