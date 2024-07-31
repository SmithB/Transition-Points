from tkinter import filedialog
import shutil
import os


def download_files():
    directory = filedialog.askdirectory()

    source_directory = os.path.join(os.getcwd(), "assets")
    files = ['new_points.csv', 'warnings.txt']
    for filename in files:
        source_path = os.path.join(source_directory, filename)
        destination_path = os.path.join(directory, filename)
        shutil.copy(source_path, destination_path)