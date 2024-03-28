# Forked from https://github.com/jhaakma/toml-editor
# Completely rewritten to prompt user for file to process and save to a new or existing file

import os
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import *
import toml, json


title = "Benchmark Configuration Editor"
window_size = "1000x900"

global toml_path, config, toml_settings, fields, path

toml_settings = {}

def process_file():
    toml_settings, toml_path = get_settings()

    # Read the list of settings from a TOML file
    print(f"path: {toml_path}")
    with open(toml_path, "r") as f:
        if toml_path.endswith('.toml'):
            config = toml.load(f)
        elif toml_path.endswith('.json'):
            config = json.load(f)

    load_editor(config, fields, inner_frame)

def load_editor(config, fields, inner_frame):

    render_settings(config, fields, inner_frame)

    frame.pack(side="top", fill="both", expand=True)
    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create a frame to hold the save button
    button_frame = Frame(frame)
    button_frame.pack(side="bottom", pady=10)

    save_button = Button(button_frame, text="Update Configuration", command=save_settings)
    save_button.pack()

    new_label = Label(button_frame, text="New File Path")
    new_label.pack()

    new_filename = Text(button_frame, width=100, height=5)
    new_filename.insert(END, path)
    new_filename.pack()

    new_button = Button(button_frame, text="New Configuration at New File Path", command=new_settings)
    new_button.pack()

def get_settings_path():
    # Check if the script is running from a PyInstaller bundle
    # if getattr(sys, 'frozen', False):
    #     # Return the path to the bundled settings.toml
    #     return os.path.join(sys._MEIPASS, 'settings.toml')
    # else:
    #     # Return the path to the settings.toml in the source directory
    #     return os.path.abspath(os.path.join(os.path.dirname(__file__), 'settings.toml'))
    return askopenfilename()    

def get_settings():
    try:
        with open(get_settings_path(), 'r') as f:
            toml_settings = toml.load(f)
            return toml_settings, f.name
    except FileNotFoundError:
        return toml_settings
    
def render_settings(current_settings, current_fields, parent_frame):
    row = 0
    for key, value in current_settings.items():
        if isinstance(value, dict):
            current_fields[key] = {}
            # If the value is a table, create a new section
            section_frame = LabelFrame(parent_frame, text=key)
            section_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            render_settings(value, current_fields[key], section_frame)
            row += 1
        else:
            # Otherwise, create a label and an entry field for the setting
            label = Label(parent_frame, text=key)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            if isinstance(value, bool):
                var = BooleanVar(value=value)
                checkbox = Checkbutton(parent_frame, variable=var)
                checkbox.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = var.get()
                checkbox.bind("<Button-1>", lambda event, key=key: current_fields.__setitem__(key, not current_settings[key].get()))
            elif isinstance(value, (int, float)):
                var = StringVar(value=str(value))
                entry = Entry(parent_frame, textvariable=var, width=20)
                entry.config(validate="key", validatecommand=(root.register(validate_number_input), '%P'))
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                current_settings[key] = var
                current_fields[key] = eval(var.get())
                entry.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, eval(current_settings[key].get())))
            # else if array
            elif isinstance(value, list):
                current_fields[key] = value
                text = Text(parent_frame, width=50, height=len(value))
                text.grid(row=row,   column=1, sticky="w", padx=5, pady=5)

                # insert each item in the list on a separate line
                for item in value:
                    text.insert(END, item)
                    text.insert(END, "\n")

                # function to update the list when the user edits it
                def update_list(event, key):
                    # get the edited list from the Text widget
                    edited_list = text.get("1.0", END).strip().split("\n")

                    # update the current_fields dictionary with the edited list
                    current_fields[key] = edited_list

                text.bind("<KeyRelease>", lambda event, key=key: update_list(event, key))
            else:
                # set height based on number of characters plus some padding
                height = int(len(str(value)) / 40) + 1


                current_fields[key] = value
                text = Text(parent_frame, width=50, height=height)
                text.insert(END, value)
                text.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                text.bind("<KeyRelease>", lambda event, key=key: current_fields.__setitem__(key, text.get("1.0", END).strip()))

            row += 1

def validate_number_input(input_value):
    # Allow empty input
    if input_value == "":
        return True

    # Try to convert input to a number
    try:
        float(input_value)
    except ValueError:
        # Input is not a number
        return False

    return True

# Update the TOML file with the new settings
def save_settings():
    with open(path, "w") as f:
        if path.endswith('.toml'):
            toml.dump(fields, f)
        elif path.endswith('.json'):
            json.dump(fields, f, indent=4)
        else:
            raise Exception("Invalid file type")
    root.destroy()
        
# Update the TOML file with the new settings
def new_settings():
    new_path = new_filename.get("1.0", "end-1c")
    print(f"File name for new configuration: {new_path}")
    with open(new_path, "w") as f:
        if path.endswith('.toml'):
            toml.dump(fields, f)
        elif path.endswith('.json'):
            json.dump(fields, f, indent=4)
        else:
            raise Exception("Invalid file type")
    root.destroy()

root = Tk()
root.title(title)
# use window_size or 450x900 as default
root.geometry(window_size)

# Center the window 1/3 of the way up the screen
window_height = 500
window_width = 900
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() - (root.winfo_screenheight()/3)
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

# Set up the main menu
menu_bar = Menubutton ( root, text="Menu" )
menu_bar.menu = Menu ( menu_bar, tearoff = 0 )
menu_bar["menu"] = menu_bar.menu
menu_bar.menu.add_command (label="Select File", command=process_file)
menu_bar.menu.add_command (label="Exit", command=root.quit)
menu_bar.pack(fill="x")

# menu_bar.add_cascade(label="File", menu=file_menu)
# file_menu.add_command(label="Exit", command=root.quit)
# file_menu.add_command(label="Open", command=process_file)

# Create a frame to hold the canvas and settings
frame = Frame(root)

# Create a canvas to hold the settings
canvas = Canvas(frame)

scrollbar = Scrollbar(canvas, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# # Create a frame inside the canvas to hold the settings
inner_frame = Frame(scrollable_frame)
inner_frame.pack(side="top", fill="both")

# Add the settings to the inner frame and track changes
# Add the settings to the inner frame and track changes
fields = {}

root.mainloop()