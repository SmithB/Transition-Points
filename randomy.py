import os.path
import random
from shapely import LineString
import tkinter as tk
from tkinter import filedialog
import os
import shutil

# df = filedialog.askopenfilename(title='Select location to download files')
# print(df)

# def copy_files_to_directory(source_directory, destination_directory):
#     files = ['new_points.csv', 'warnings.txt']
#     for filename in files:
#         source_path = os.path.join(source_directory, filename)
#         destination_path = os.path.join(destination_directory, filename)
#         shutil.copy(source_path, destination_path)


def copy_files_to_directory():
    global root
    directory = filedialog.askdirectory(title='orankjkjkges')

    source_directory = os.path.join(os.getcwd(), "assets")
    # copy_files_to_directory(source_directory, directory)
    files = ['new_points.csv', 'warnings.txt']
    for filename in files:
        source_path = os.path.join(source_directory, filename)
        destination_path = os.path.join(directory, filename)
        shutil.copy(source_path, destination_path)

    root.withdraw()
    root.quit()

def run():
    global root
    root = tk.Tk()
    root.title("Select a folder to download assets files")
    root.geometry("400x300")
    copy_files_to_directory()

run()
# root.quit()
# directory = filedialog.askdirectory(title='orankjkjkges')
#
# source_directory = os.path.join(os.getcwd(), "assets")
# copy_files_to_directory(source_directory, directory)

# root.withdraw()
# files = {
#     "Transition Points.csv": "/assets/new_points.csv",
#     "Warnings.txt": "/assets/warnings.txt"
# }
# for name, path in files.items():
#     with open(os.path.join(directory, name), 'wb') as file:
#         file.
rgts = []

while len(rgts) != 30:
    rand = random.randrange(1, 1388)
    if rand not in rgts:
        rgts.append(rand)
rgts.sort()
print(rgts)


# LineString((-179.9985612572251, 0.002678469888111313))


# print(186+69)