import os
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar
from cleaner import scan_and_clean

# --- Color Palette Constants ---

BG = "#fbfcfc"
PRIMARY = "#59b09d"
SECONDARY = "#97d9ca"
ACCENT = "#71d8c1"
TEXT= "#070908"  

# Creates default window dimensions and titles it

window = Tk()
window.title("Desktop Declutter")
window.geometry("750x750")
window.config(padx=20, pady=20, bg=BG)
window.resizable(False, False)

# Sets logo

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "Logo.png")

try:

    app_icon = PhotoImage(file=logo_path)
    window.iconphoto(True, app_icon)

except Exception as e:

    print(f"Could not load icon: {e}")

# Creates label of application

lbl = Label(

    window,
    text="Desktop Declutter",
    font=("Arial Bold", 20),
    bg=BG,
    fg=TEXT

)
lbl.pack(pady=20)

# Section for selecting a folder to declutter

folder_selected = "No folder was selected"

def choose_folder():

        global folder_selected
        folder_selected = filedialog.askdirectory(title="Select a Folder to Declutter")

        if folder_selected:

            path_label.config(text=folder_selected)
            log_message(f"Folder Selected: {folder_selected}")

        else:

            folder_selected = "No folder was selected"



row_frame = Frame(window)
row_frame.pack(pady=20, fill="x")

btn = Button(

     row_frame,
     text="Select Folder",
     command=choose_folder,
     bg=PRIMARY,
     fg="white",
     activebackground=ACCENT,
     relief="flat",
     padx=12,
     pady=6,
     cursor="hand2"

)

btn.pack(side=LEFT, padx=(0, 15))

path_label = Label(

     row_frame,
     text="No folder selected",
     wraplength=350

)

path_label.pack(side=LEFT)

# Start button section

def start_declutter():

     if folder_selected == "No folder was selected":

          log_message("Please select a folder first!")
          return

     scan_and_clean(folder_selected, log_message)



start_btn = Button(

     window,
     text="Start Declutter",
     font=("Arial Bold", 12),
     command=start_declutter,
     bg=PRIMARY,
     fg="white",
     activebackground=ACCENT,
     relief="flat",
     padx=20,
     pady=10,
     cursor="hand2"

)

start_btn.pack(fill="x", pady=20)

# section for creating bottom frame

bottom_frame = Frame(window)
bottom_frame.pack(pady=20, fill="both", expand=True)

# section for creating options frame

options_frame = Frame(bottom_frame)
options_frame.pack(side=LEFT, fill="y", pady=20)

#section for options label

options_label = Label(

    options_frame,
    text="Options",
    font=("Arial Bold", 15),
    fg=PRIMARY,

)
options_label.pack(pady=20)

# Delete empty folders section

delete_empty_var = BooleanVar(value=False)

def on_toggle():
     log_message(f"Delete empty folders was set to: {delete_empty_var.get()}")

delete_empty_check = Checkbutton(

     options_frame,
     text="Delete Empty Folders",
     bg=PRIMARY,
     fg=BG,
     activebackground=ACCENT,
     selectcolor=ACCENT,
     variable=delete_empty_var,
     command=on_toggle,
     cursor="hand2",
     relief="flat",
     padx=10,
     pady=5,

)
delete_empty_check.pack(side=TOP)

# message box section

msg_box = scrolledtext.ScrolledText(

     bottom_frame,
     width=50,
     height=8,
     font=("Segoe UI", 9),
     bg="#f0f4f3",
     fg=TEXT,
     relief="solid",
     bd=1,
     state="disabled"

)

msg_box.pack(fill="both", expand=True, pady=20)

def log_message(message: str):

    msg_box.config(state="normal")      
    msg_box.insert(END, message + "\n")
    msg_box.see(END)                    
    msg_box.config(state="disabled")

# Set initial message and lock the box

log_message("Select a folder to get started")

# Keeps window opened

window.mainloop() 
