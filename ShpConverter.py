import os
import geopandas as gpd
from fiona.drvsupport import supported_drivers

supported_drivers['KML'] = 'rw'


def shp_to_kml(shapefile):
    """
    Converts shapefile to KML
    :param shapefile: file path
    :return:
    """
    read_shp = gpd.read_file(shapefile)
    new_filepath = os.path.join('Public', 'Mask.kml')
    read_shp.to_file(new_filepath, driver='KML')
    return new_filepath
