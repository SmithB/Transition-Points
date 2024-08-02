import os.path
import random
import time

from shapely import LineString
import tkinter as tk
from tkinter import filedialog
import os
import shutil

rgts = []

while len(rgts) != 30:
    rand = random.randrange(1, 1388)
    if rand not in rgts:
        rgts.append(rand)
rgts.sort()
print(rgts)


# LineString((-179.9985612572251, 0.002678469888111313))


# print(186+69)