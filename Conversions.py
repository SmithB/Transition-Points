from pyproj import Transformer


to_gcs_transform = Transformer.from_crs("EPSG:3857", "EPSG:4326")
to_cartesian_transform = Transformer.from_crs("EPSG:4326", "EPSG:3857")


def gcs_list_to_cartesian(gcs_list):
    """
    This function coverts a given list of gcs coordinates to a list of cartesian coordinates
    :param gcs_list: list of tuples containing (latitude, longitude)
    :return: list of tuples containing (x, y)
    """
    cartesian_list = []
    for coordinates in gcs_list:
        cartesian_list.append(gcs_to_cartesian(coordinates[1], coordinates[0]))
    return cartesian_list


#  check if this works

def cartesian_list_to_gcs(cartesian_list):
    """
    This function converts a given list of cartesian coordinates to a list of gcs coordinates
    :param cartesian_list: list of tuples containing (x, y)
    :return: list of tuples containing (latitude, longitude)
    """
    gcs_list = []
    for coordinates in cartesian_list:
        gcs_list.append(cartesian_to_gcs(coordinates[0], coordinates[1]))
    return cartesian_list


def gcs_to_cartesian(latitude, longitude):
    """
    This function converts latitude and longitude to cartesian coordinates
    :param latitude: latitude coordinate of EPSG:4326 format
    :param longitude: longitude coordinate of EPSG:4326 format
    :return: tuple of (x, y) of EPSG:3857 format
    """
    cart_coordinates = to_cartesian_transform.transform(latitude, longitude)
    return cart_coordinates


def cartesian_to_gcs(x, y):
    """
    This function converts the given x and y coordinates to latitude and longitude
    :param x: x coordinate of EPSG:3857 format
    :param y: y coordinate of EPSG:3857 format
    :return: tuple of (latitude, longitude) of EPSG:4326
    """
    gcs_coordinates = to_gcs_transform.transform(x, y)
    return gcs_coordinates


# print(gcs_to_cartesian(90, 180))

# x = 4328369.131354082
# y = 4997071.061740645
#
# # WGS84 is EPSG:4326

# print(transformer.transform(x, y))
#
# lat = 40.89638903854909
# long = 38.88240146006508

# print(other_trans.transform(lat, long))