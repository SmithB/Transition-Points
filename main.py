from Point import Point, TypePoint
import CsvHandler as Ch

# Get files --- Upload probably
# transition_csv = input('Enter in file path for csv: ')
# kml_file = input('Enter in file path for kml: ')

points_dict = {}
for i in range(1, 1388):
    points_dict[i] = []

points_dict = Ch.read_csv('/Users/pvelmuru/PycharmProjects/Transistion Points/RGT_transition_locations_V2.0 1.csv', points_dict)
print(len(points_dict[17]))
Ch.write_csv('testwrite.csv', points_dict)
# Read files
# Receive current point objects
# Process kml file
# find intersections
# Redo Points
# Output as csv file







# print(TypePoint.VEGETATION.value)
# one = Point(14, TypePoint.RGT, 23.3, 45.6)
# print(one.state.value)