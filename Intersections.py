from shapely import LineString, Polygon, MultiPolygon
import shapely
import Conversions


def find_intersections(geometry1, geometry2):
    # TODO remove function?
    intersection = shapely.make_valid(geometry1.intersection(geometry2))
    return intersection


def modify_land_mask(land_mask, rgt_mask):
    """
    This functions generates a new land mask MultiPolygon that no longer includes any overlap with
    the rgt mask area ???CARTESIAN???
    :param land_mask: MultiPolygon mask that represent most land
    :param rgt_mask: MultiPolygon or Polygon that needs rgt tracking
    :return: A Multipolygon that is the new land mask that takes into account rgt mask
    """
    intersection = rgt_mask.intersection(land_mask)
    # TODO add in error checking. If not necessarily multipolygon
    new_land = land_mask.difference(intersection)
    new_land_cart = [Polygon(Conversions.cartesian_list_to_gcs(polygon.exterior.coords)) for polygon in new_land.geoms]
    new_land_multipolygon = MultiPolygon(new_land_cart)
    return new_land_multipolygon
