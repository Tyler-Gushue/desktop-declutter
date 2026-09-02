import os
import json
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from tkinter.ttk import Progressbar, Style, Combobox, Treeview
import threading
from cleaner import scan_and_clean, undo_last_declutter

# --- Color Palette Constants ---

BG = "#fbfcfc"
PRIMARY = "#59b09d"
SECONDARY = "#97d9ca"
ACCENT = "#71d8c1"
TEXT = "#070908"

# --- JSON Configuration & Persistence ---

script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(script_dir, "config.json")

DEFAULT_CONFIG = {
    "settings": {
        "never_show_again_delete_prompt": False
    },
    "presets": {
        "Default": {
            "sort_uncategorized_to_other": True,
            "categories": {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
                "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx"],
                "Media": [".mp4", ".mov", ".mp3", ".wav"],
                "Archives": [".zip", ".rar", ".7z", ".tar"],
                "Code": [".py", ".js", ".html", ".css", ".json"]
            }
        },
        "School Projects": {
            "sort_uncategorized_to_other": True,
            "categories": {
                "Assignments": [".pdf", ".docx", ".txt"],
                "Presentations": [".pptx", ".key"],
                "Code": [".py", ".java", ".cpp", ".sql"]
            }
        },
        "Media & Assets": {
            "sort_uncategorized_to_other": False,
            "categories": {
                "Graphics": [".png", ".jpg", ".svg", ".psd"],
                "Audio": [".mp3", ".wav", ".flac"],
                "Video": [".mp4", ".mov", ".mkv"]
            }
        }
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if "presets" in data and "settings" in data:
                    return data
        except Exception as e:
            print(f"Error loading config.json: {e}")
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving config.json: {e}")

# Load persistent config state
app_config = load_config()
app_presets = app_config["presets"]

# Creates default window dimensions and titles it

window = Tk()
window.title("Desktop Declutter")
window.geometry("750x750")
window.config(padx=20, pady=20, bg=BG)
window.resizable(False, False)

# Sets logo

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

# --- Preset Selection Section ---

preset_frame = Frame(window, bg=BG)
preset_frame.pack(fill="x", pady=(0, 15))

preset_label = Label(
    preset_frame,
    text="Sorting Preset:",
    font=("Arial Bold", 10),
    bg=BG,
    fg=TEXT
)
preset_label.pack(side=LEFT, padx=(0, 10))

current_preset_var = StringVar(value="Default")

preset_dropdown = Combobox(
    preset_frame,
    textvariable=current_preset_var,
    values=list(app_presets.keys()),
    state="readonly",
    font=("Arial", 10)
)
preset_dropdown.pack(side=LEFT, fill="x", expand=True, padx=(0, 10))

def on_preset_change(event):
    log_message(f"Active preset changed to: {current_preset_var.get()}")

preset_dropdown.bind("<<ComboboxSelected>>", on_preset_change)

def open_manage_presets():
    open_preset_manager_modal(window)

def open_preset_manager_modal(parent):
    modal = Toplevel(parent)
    modal.title("Manage Presets")
    modal.geometry("540x460")
    modal.config(padx=20, pady=20, bg=BG)
    modal.resizable(False, False)
    modal.transient(parent)
    modal.grab_set()

    header_frame = Frame(modal, bg=BG)
    header_frame.pack(fill="x", pady=(0, 15))

    Label(
        header_frame,
        text="Manage Presets",
        font=("Arial Bold", 16),
        bg=BG,
        fg=TEXT
    ).pack(side=LEFT)

    def add_new_preset():
        new_name = simpledialog.askstring("New Preset", "Enter a name for the new preset:", parent=modal)
        if new_name and new_name.strip():
            name = new_name.strip()
            if name in app_presets:
                messagebox.showwarning("Exists", "A preset with this name already exists.", parent=modal)
                return
            app_presets[name] = {
                "sort_uncategorized_to_other": True,
                "categories": {
                    "Documents": [".pdf", ".txt", ".docx"],
                    "Images": [".png", ".jpg"]
                }
            }
            save_config(app_config)
            preset_dropdown["values"] = list(app_presets.keys())
            refresh_preset_rows()

    Button(
        header_frame,
        text="+ New Preset",
        command=add_new_preset,
        bg=PRIMARY,
        fg="white",
        activebackground=ACCENT,
        relief="flat",
        padx=10,
        pady=4,
        font=("Arial Bold", 9),
        cursor="hand2"
    ).pack(side=RIGHT)

    list_container = Frame(modal, bg=BG)
    list_container.pack(fill="both", expand=True, pady=(0, 15))

    def refresh_preset_rows():
        for widget in list_container.winfo_children():
            widget.destroy()

        for name in app_presets.keys():
            render_preset_row(name, is_default=(name == "Default"))

    def render_preset_row(name, is_default=False):
        row = Frame(list_container, bg="#f0f4f3", padx=12, pady=10)
        row.pack(fill="x", pady=4)

        Label(
            row,
            text=name,
            font=("Segoe UI Bold", 10),
            bg="#f0f4f3",
            fg=TEXT
        ).pack(side=LEFT)

        def delete_preset(target_name):
            if messagebox.askyesno("Delete Preset", f"Delete preset '{target_name}'?", parent=modal):
                del app_presets[target_name]
                save_config(app_config)
                preset_dropdown["values"] = list(app_presets.keys())
                if current_preset_var.get() == target_name:
                    current_preset_var.set("Default")
                refresh_preset_rows()

        if not is_default:
            Button(
                row,
                text="Delete",
                command=lambda n=name: delete_preset(n),
                bg="#e07a5f",
                fg="white",
                relief="flat",
                padx=8,
                pady=2,
                cursor="hand2",
                font=("Segoe UI", 9)
            ).pack(side=RIGHT, padx=(6, 0))

        Button(
            row,
            text="Edit Categories",
            bg=PRIMARY,
            fg="white",
            command=lambda n=name: open_manage_categories(n),
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            font=("Segoe UI", 9)
        ).pack(side=RIGHT)

    refresh_preset_rows()

    Button(
        modal,
        text="Close",
        command=modal.destroy,
        bg="#999999",
        fg="white",
        relief="flat",
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=BOTTOM, fill="x")

manage_btn = Button(
    preset_frame,
    text="⚙ Manage Presets",
    command=open_manage_presets,
    bg=PRIMARY,
    fg="white",
    activebackground=ACCENT,
    relief="flat",
    padx=10,
    pady=3,
    cursor="hand2",
    font=("Arial Bold", 9)
)
manage_btn.pack(side=RIGHT)

# --- Preset -> Categories & Extensions Modal ---

def open_manage_categories(preset_name="Default"):
    open_categories_manager_modal(window, preset_name)

def open_categories_manager_modal(parent, preset_name):
    modal = Toplevel(parent)
    modal.title(f"Edit Preset - {preset_name}")
    modal.geometry("580x520")
    modal.config(padx=20, pady=20, bg=BG)
    modal.resizable(False, False)
    modal.transient(parent)
    modal.grab_set()

    # Header Bar showing Preset Title
    header_frame = Frame(modal, bg=BG)
    header_frame.pack(fill="x", pady=(0, 10))

    title_box = Frame(header_frame, bg=BG)
    title_box.pack(side=LEFT)

    Label(
        title_box,
        text=f"Editing: {preset_name}",
        font=("Arial Bold", 15),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w")

    Label(
        title_box,
        text="Manage target folders and assigned extensions",
        font=("Segoe UI", 9),
        bg=BG,
        fg="#666666"
    ).pack(anchor="w")

    def add_new_category():
        cat_name = simpledialog.askstring("New Directory", "Enter folder name (e.g., Spreadsheets):", parent=modal)
        if cat_name and cat_name.strip():
            cat = cat_name.strip()
            preset_cats = app_presets[preset_name]["categories"]
            if cat in preset_cats:
                messagebox.showwarning("Exists", "A folder with this name already exists in this preset.", parent=modal)
                return
            preset_cats[cat] = []
            save_config(app_config)
            refresh_categories()

    Button(
        header_frame,
        text="+ Add Directory",
        command=add_new_category,
        bg=PRIMARY,
        fg="white",
        activebackground=ACCENT,
        relief="flat",
        padx=10,
        pady=4,
        font=("Arial Bold", 9),
        cursor="hand2"
    ).pack(side=RIGHT)

    # Categories List Container
    cat_list_frame = Frame(modal, bg=BG)
    cat_list_frame.pack(fill="both", expand=True, pady=(10, 10))

    def refresh_categories():
        for widget in cat_list_frame.winfo_children():
            widget.destroy()

        categories = app_presets[preset_name].get("categories", {})
        for cat_name, extensions in categories.items():
            render_category_row(cat_name, extensions)

    def edit_extensions(category_name):
            curr_exts = ", ".join(app_presets[preset_name]["categories"].get(category_name, []))
            user_input = simpledialog.askstring(
                f"Edit Extensions - {category_name}",
                f"Enter comma-separated extensions for {category_name}:\n(e.g., .png, .jpg, .svg)",
                initialvalue=curr_exts,
                parent=modal
            )
            if user_input is None:
                return

            raw_items = [e.strip().lower() for e in user_input.split(",") if e.strip()]
            new_exts = []
            for ext in raw_items:
                if not ext.startswith("."):
                    ext = "." + ext
                if ext not in new_exts:
                    new_exts.append(ext)

            # Check for conflicts across other categories in the same preset
            all_categories = app_presets[preset_name]["categories"]
            conflicts = {}  # {ext: other_category_name}

            for ext in new_exts:
                for other_cat, exts_list in all_categories.items():
                    if other_cat != category_name and ext in exts_list:
                        conflicts[ext] = other_cat

            if conflicts:
                conflict_details = "\n".join([f"• {ext} (currently in '{cat}')" for ext, cat in conflicts.items()])
                reassign = messagebox.askyesnocancel(
                    "Duplicate Extensions Detected",
                    f"The following extension(s) are already used in other categories:\n\n"
                    f"{conflict_details}\n\n"
                    f"• Click 'Yes' to reassign them to '{category_name}'.\n"
                    f"• Click 'No' to keep them in their original folders and skip adding them here.\n"
                    f"• Click 'Cancel' to abort.",
                    parent=modal
                )

                if reassign is None:
                    return  # Abort edit

                if reassign:
                    # Remove conflicting extensions from their old categories
                    for ext, other_cat in conflicts.items():
                        if ext in all_categories[other_cat]:
                            all_categories[other_cat].remove(ext)
                else:
                    # Discard conflicting extensions from being added here
                    new_exts = [ext for ext in new_exts if ext not in conflicts]

            app_presets[preset_name]["categories"][category_name] = new_exts
            save_config(app_config)
            refresh_categories()

    def delete_category(category_name):
        if messagebox.askyesno("Delete Directory", f"Remove folder category '{category_name}'?", parent=modal):
            del app_presets[preset_name]["categories"][category_name]
            save_config(app_config)
            refresh_categories()

    def render_category_row(cat_name, extensions):
        row = Frame(cat_list_frame, bg="#f0f4f3", padx=12, pady=8)
        row.pack(fill="x", pady=3)

        info_box = Frame(row, bg="#f0f4f3")
        info_box.pack(side=LEFT, fill="x", expand=True)

        Label(
            info_box,
            text=cat_name,
            font=("Segoe UI Bold", 10),
            bg="#f0f4f3",
            fg=TEXT
        ).pack(anchor="w")

        ext_preview = ", ".join(extensions) if extensions else "No extensions assigned"
        Label(
            info_box,
            text=ext_preview,
            font=("Segoe UI", 8),
            bg="#f0f4f3",
            fg="#555555",
            wraplength=280,
            justify="left"
        ).pack(anchor="w")

        Button(
            row,
            text="Delete",
            command=lambda c=cat_name: delete_category(c),
            bg="#e07a5f",
            fg="white",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            font=("Segoe UI", 9)
        ).pack(side=RIGHT, padx=(6, 0))

        Button(
            row,
            text="Edit Extensions",
            command=lambda c=cat_name: edit_extensions(c),
            bg=PRIMARY,
            fg="white",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            font=("Segoe UI", 9)
        ).pack(side=RIGHT)

    refresh_categories()

    # Sort Uncategorized Checkbox
    sort_other_var = BooleanVar(value=app_presets[preset_name].get("sort_uncategorized_to_other", True))

    def on_toggle_other():
        app_presets[preset_name]["sort_uncategorized_to_other"] = sort_other_var.get()
        save_config(app_config)

    other_check = Checkbutton(
        modal,
        text="Sort all uncategorized file types into 'Other' folder",
        bg=BG,
        fg=TEXT,
        activebackground=BG,
        selectcolor="white",
        variable=sort_other_var,
        command=on_toggle_other,
        font=("Segoe UI", 9),
        cursor="hand2"
    )
    other_check.pack(anchor="w", pady=(0, 15))

    Button(
        modal,
        text="Done",
        command=modal.destroy,
        bg="#999999",
        fg="white",
        relief="flat",
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=BOTTOM, fill="x")

# Start button section

last_moved_history = []

def start_declutter():
    if folder_selected == "No folder was selected":
        log_message("Please select a folder first!")
        return

    start_btn.config(state="disabled")
    progress_bar["value"] = 0

    def run_scan():
        global last_moved_history
        active_preset_name = current_preset_var.get()
        preset_info = app_presets.get(active_preset_name, app_presets.get("Default"))

        last_moved_history = scan_and_clean(
            folder_selected,
            delete_empty_var.get(),
            delete_only_var.get(),
            delete_duplicates_var.get(),
            preset_data=preset_info,
            log_func=log_message,
            progress_callback=update_progress
        )

        # Re-enable start button when finished
        start_btn.config(state="normal")

        # Enable undo button if files were moved
        if last_moved_history:
            undo_btn.config(state="normal", bg="#999999", cursor="hand2")

    threading.Thread(target=run_scan, daemon=True).start()

start_btn = Button(
    window,
    text="Start Scan",
    font=("Arial Bold", 12),
    command=start_declutter,
    bg=PRIMARY,
    fg="white",
    activebackground=ACCENT,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=10,
    cursor="hand2"
)
start_btn.pack(fill="x", pady=(15, 3))

# section for undo button

def undo_declutter():
    global last_moved_history

    if not last_moved_history:
        return

    start_btn.config(state="disabled")
    undo_btn.config(state="disabled", bg="#cccccc", cursor="")
    progress_bar["value"] = 0

    def run_undo():
            global last_moved_history
            active_preset_name = current_preset_var.get()
            preset_info = app_presets.get(active_preset_name, app_presets.get("Default"))

            undo_last_declutter(
                folder_selected, 
                last_moved_history, 
                preset_data=preset_info, 
                log_func=log_message, 
                progress_callback=update_progress
            )
            last_moved_history = []
            start_btn.config(state="normal")

    threading.Thread(target=run_undo, daemon=True).start()

undo_btn = Button(
    window,
    text="Undo Sort",
    font=("Arial Bold", 12),
    command=undo_declutter,
    bg="#cccccc",
    fg="white",
    activebackground="#999999",
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=10,
    state="disabled"
)
undo_btn.pack(fill="x", pady=(3, 15))

# section for progress bar

def update_progress(current_item: int, total_items: int):
    progress_bar["maximum"] = total_items
    progress_bar["value"] = current_item

style = Style()
style.theme_use("clam")

style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor=BG,
    background=ACCENT,
    bordercolor="#f0f4f3",
    lightcolor=ACCENT,
    darkcolor=ACCENT,
)

progress_bar = Progressbar(
    window,
    orient="horizontal",
    mode="determinate",
    style="Custom.Horizontal.TProgressbar"
)
progress_bar.pack(fill="x", pady=(0, 10))

# section for creating bottom frame

bottom_frame = Frame(window)
bottom_frame.pack(pady=20, fill="both", expand=True)

# section for creating options frame

options_frame = Frame(bottom_frame)
options_frame.pack(side=LEFT, fill="y", pady=20)

# section for options label

options_label = Label(
    options_frame,
    text="Options",
    font=("Arial Bold", 15),
    fg=PRIMARY,
)
options_label.pack(pady=20)

# Delete only mode section

delete_only_var = BooleanVar(value=False)

def on_toggle():
    log_message(f"Delete only mode was set to: {delete_only_var.get()}")

delete_only_check = Checkbutton(
    options_frame,
    text="Delete Only Mode",
    bg=PRIMARY,
    fg=BG,
    activebackground=ACCENT,
    selectcolor=ACCENT,
    variable=delete_only_var,
    command=on_toggle,
    cursor="hand2",
    relief="flat",
    anchor="w",
    padx=10,
    pady=5,
)
delete_only_check.pack(side=TOP, fill="x")

# Delete empty folders section

delete_empty_var = BooleanVar(value=False)

def on_toggle_empty():
    log_message(f"Delete empty folders was set to: {delete_empty_var.get()}")

delete_empty_check = Checkbutton(
    options_frame,
    text="Delete Empty Folders",
    bg=PRIMARY,
    fg=BG,
    activebackground=ACCENT,
    selectcolor=ACCENT,
    variable=delete_empty_var,
    command=on_toggle_empty,
    cursor="hand2",
    relief="flat",
    padx=10,
    pady=5,
)
delete_empty_check.pack(side=TOP)

# Delete duplicates mode section

delete_duplicates_var = BooleanVar(value=False)

def on_toggle_duplicates():
    log_message(f"Delete duplicates was set to: {delete_duplicates_var.get()}")

delete_duplicates_check = Checkbutton(
    options_frame,
    text="Delete Duplicates",
    bg=PRIMARY,
    fg=BG,
    activebackground=ACCENT,
    selectcolor=ACCENT,
    variable=delete_duplicates_var,
    command=on_toggle_duplicates,
    cursor="hand2",
    relief="flat",
    anchor="w",
    padx=10,
    pady=5,
)
delete_duplicates_check.pack(side=TOP, fill="x")

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