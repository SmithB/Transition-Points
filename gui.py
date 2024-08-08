"""
Module contains function to create GUI to process user inputs
Author: Pranesh Velmurugan praneshsvels@gmail.com
Date: 8/5/24
"""

import tkinter as tk
from tkinter import filedialog, simpledialog

# Global variables to store user inputs
mask_filetype = None
mask_region_type = None
mask_filepath = None
transition_csv_path = None
files_destination = None
threshold_kilometers = None


def processing(param):
    """
    Removes question label and buttons the '~2 min' question
    :param param: Ignores given parameter
    """
    proceed_to_next(question_label, *buttons)


def set_mask_filetype(filetype):
    global mask_filetype
    mask_filetype = filetype
    proceed_to_next(question_label, *buttons)


def set_mask_region_type(region_type):
    global mask_region_type
    mask_region_type = region_type
    proceed_to_next(question_label, *buttons)


def select_mask_filepath():
    global mask_filepath
    mask_filepath = filedialog.askopenfilename(title="Select Mask File")
    if mask_filepath:
        proceed_to_next(question_label, button)


def select_transition_csv():
    global transition_csv_path
    transition_csv_path = filedialog.askopenfilename(title="Select Transition Point CSV File")
    if transition_csv_path:
        proceed_to_next(question_label, button)


def enter_threshold_kilometers():
    global threshold_kilometers
    threshold_kilometers = simpledialog.askfloat("Enter Threshold Kilometers", "Enter Threshold Kilometers:")
    if threshold_kilometers is not None:
        proceed_to_next(button)


def select_files_folder():
    global files_destination
    files_destination = filedialog.askdirectory(title="Select Folder to Store Files")
    if files_destination:
        proceed_to_next(question_label, button)


def proceed_to_next(*widgets):
    for widget in widgets:
        widget.pack_forget()
    step()


# List of lambda functions that are the steps that the GUI follows
steps = [
    lambda: setup_question("The program will take ~2 mins to process", ["Continue"], processing),
    lambda: setup_question("Is the mask a kml file or shapefile?", ["KML", "Shapefile"], set_mask_filetype),
    lambda: setup_question("Is the mask region an off-pointing or RGT region?", ["Off-Pointing", "RGT"], set_mask_region_type),
    lambda: setup_file_selection("Select mask file:", select_mask_filepath),
    lambda: setup_file_selection("Select Transition Point csv file:", select_transition_csv),
    lambda: setup_folder_selection("Select Folder to Store Files", select_files_folder),
    lambda: setup_threshold_kilometers()
]


def setup_question(question, options, command):
    global question_label, buttons
    question_label = tk.Label(root, text=question)
    question_label.pack(pady=10)
    buttons = [tk.Button(root, text=option, command=lambda option=option: command(option)) for option in options]
    for button in buttons:
        button.pack(pady=5)


def setup_file_selection(question, command):
    global question_label, button
    question_label = tk.Label(root, text=question)
    question_label.pack(pady=10)
    button = tk.Button(root, text="Select File", command=command)
    button.pack(pady=5)


def setup_folder_selection(question, command):
    global question_label, button
    question_label = tk.Label(root, text=question)
    question_label.pack(pady=10)
    button = tk.Button(root, text="Select Folder", command=command)
    button.pack(pady=5)


def setup_threshold_kilometers():
    enter_threshold_kilometers()


def step():
    """
    Progresses through the steps of the GUI
    """
    if steps:
        steps.pop(0)()
    else:
        root.withdraw()
        root.quit()
        root.destroy()


def run():
    """
    Function initializes GUI
    """
    global root
    root = tk.Tk()
    root.title("Transition Point Modifier")
    root.geometry("400x300")

    step()

    root.mainloop()
