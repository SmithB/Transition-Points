from shapely import LineString, Polygon

#  Maybe use union to convert the mask multipolygon into a singular polygon

def find_intersections(geometry1, geometry2):
    intersection = geometry1.intersection(geometry2)
    return list(intersection.geoms)


def modify_ocean_mask(ocean_mask, rgt_mask):
    intersection = find_intersections(ocean_mask, rgt_mask)


a = LineString([(0, 0), (1, 1), (1,2), (2,2)])
b = LineString([(0, 0), (1, 1), (2,1), (2,2)])
x = a.intersection(b)

print(x)
print(find_intersections(a, b))
