import random
from shapely import LineString

rgts = []

while len(rgts) != 40:
    rand = random.randrange(1, 1388)
    if rand not in rgts:
        rgts.append(rand)
rgts.sort()
print(rgts)


LineString((-179.9985612572251, 0.002678469888111313))
