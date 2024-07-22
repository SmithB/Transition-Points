import os
import geopandas as gpd
from fiona.drvsupport import supported_drivers

# shp_folder = './Data/snow_depth_gt5cm_buffout500km_buffin400km_epsg4326'

supported_drivers['KML'] = 'rw'

# for shapefile in os.listdir(shp_folder):
#     if shapefile.endswith('.shp'):
#         print(shapefile)
#         read_shp = gpd.read_file(shp_folder+'/'+shapefile)
#         read_shp.to_file('./Data' + '/' + shapefile[:-4] + '.kml', driver='KML')


def shp_to_kml(shapefile):
    """
    Converts shapefile to KML
    :param shapefile: file path
    :return:
    """
    print(shapefile)
    read_shp = gpd.read_file(shapefile)
    index = 0
    for i in range(len(shapefile) - 1, -1, -1):
        if shapefile[i] == '/':
            index = i
            break
    new_filepath = './Data/' + shapefile[i+1:-4] + '.kml'
    read_shp.to_file(new_filepath, driver='KML')
    return new_filepath
