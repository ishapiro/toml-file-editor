# Forked from https://github.com/jhaakma/toml-editor
# Completely rewritten to prompt user for file to process and save to a new or existing file
# Integrated ttkbootstrap for a more modern look

# This script is a simple GUI for editing TOML files.  It allows the user to select a TOML file, edit the settings, and save the changes to the same or a new file.

import os
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import toml, json

# Global Variables
title = "TOML Configuration Editor"
toml_path = ""
config = {}
fields = {}
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

    # Clear the help text
    help_frame.destroy()
    
    print(f"config: {config}")
    print(f"fields: {fields}")
    
    # Put the fields on the screen
    render_settings(config, fields, inner_frame)


def get_settings_path():
    return askopenfilename()    

def get_settings():
    try:
        with open(get_settings_path(), 'r') as f:
            toml_settings = toml.load(f)
            toml_path = f.name
            new_filename.delete("1.0", 'end')  # Delete existing text from the beginning to the end
            new_filename.insert("1.0", toml_path)  # Insert new text at the beginning
            original_path.set(toml_path)
            new_button["state"] = "enabled"
            save_button["state"] = "enabled"
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
    save_path = original_path.get()
    with open(save_path, "w") as f:
        if f.name.endswith('.toml'):
            toml.dump(fields, f)
        elif f.name.endswith('.json'):
            json.dump(fields, f, indent=4)
        else:
            raise Exception("Invalid file type")
        
    clear_interframe()
        
# Update the TOML file with the new settings
def new_settings():
    new_path = new_filename.get("1.0", "end-1c")
    print(f"File name for new configuration: {new_path}||")
    with open(new_path, "w") as f:
        if f.name.endswith('.toml'):
            toml.dump(fields, f)
        elif f.name.endswith('.json'):
            json.dump(fields, f, indent=4)
        else:
            raise Exception("Invalid file type")
        
    clear_interframe()

def clear_parameters():
    return

def clear_interframe():
    for widget in inner_frame.winfo_children():
        widget.destroy()

    # Disable the buttons until we load another file
    new_button["state"] = "disabled"
    save_button["state"] = "disabled"

    # Clear the file name fields
    new_filename.delete("1.0", 'end')  # Delete existing text from the beginning to the end
    original_path.set("")


#########################################################
# Main Code Starts Here
#########################################################

root = ttk.Window(themename="minty")
root.title(title)

# Center the window 1/3 of the way up the screen
window_height = 800
window_width = 1000
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
inner_frame = Frame(scrollable_frame, width=700)
inner_frame.pack(side="top", fill="both")

frame.pack(side="top", fill="both", expand=True)
canvas.pack(side="top", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Add some help to the startup screen
help_text = """
Welcome to the TOML Configuration Editor.  \n\nTo get started, click on the "Select File" option in the menu above.  This will allow you to select a TOML file to edit.  Once you have selected a file, you can make changes to the settings and then click the "Update Above Configuration" button to save your changes.  If you want to save the changes to a new file, enter the new file name in the "New File Path" field and click the "New Configuration using the above path" button.  \n\n Enjoy!
"""

help_frame = Frame(inner_frame, width=800, height=600)
help_frame.grid(sticky="nsew", padx=100, pady=100)

help_label = Label(help_frame, text=help_text, wraplength=700, justify="center", font=("Arial", 16))
help_label.pack(pady=10, padx=10)

# Create a frame to hold the save buttons
button_frame = Frame(frame)
button_frame.pack(side="bottom", pady=10)

original_label = Label(button_frame, text="Original File Path")
original_label.pack(pady=(10,0))

original_path = StringVar()
save_path = Label(button_frame, textvariable=original_path, width=100, borderwidth=5, relief="groove")
save_path.pack()

save_button = Button(button_frame, text="Update Above Configuration", command=save_settings)
save_button.pack(pady=1)

new_label = Label(button_frame, text="New File Path")
new_label.pack(pady=(10,0))

new_filename = Text(button_frame, width=100, height=1, relief="groove")
new_filename.pack(pady=1)

new_button = Button(button_frame, text="New Configuration using the above path", command=new_settings)
new_button.pack()

# start with the buttons disabled
new_button["state"] = "disabled"
save_button["state"] = "disabled"

root.mainloop()