import os.path
import platform
import tkinter as tk
from tkinter import filedialog
import requests


def get_file_path():
    root = tk.Tk()
    root.withdraw()

    filepath = filedialog.askopenfilename()
    return filepath


def download_file(temp_file_path, file_name):
    root = tk.Tk()
    root.withdraw()

    directory = filedialog.askdirectory()
    save_path = os.path.join(directory, file_name)

    # response = requests.get(temp_file_path,
    #                         stream=True)

    with open(temp_file_path, 'r') as src, open(save_path, 'w') as dst:
        dst.write(src.read())

# file_path = get_file_path()
# print(file_path)
#
# download_file(file_path, "lop.csv")