import random

rgts = []

while len(rgts) != 40:
    rand = random.randrange(1, 1388)
    if rand not in rgts:
        rgts.append(rand)
rgts.sort()
print(rgts)
