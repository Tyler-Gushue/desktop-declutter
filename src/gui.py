import os
import json
from tkinter import *
from tkinter import filedialog, scrolledtext
from tkinter.ttk import Progressbar, Style, Combobox
import threading
from cleaner import scan_and_clean, undo_last_declutter

# --- Color Palette Constants ---

BG = "#f6faf9"          # app background
SURFACE = "#ffffff"     # card backgrounds
CARD = "#eef5f3"        # nested row backgrounds inside cards
BORDER = "#dbe8e4"      # subtle card borders
PRIMARY = "#59b09d"
PRIMARY_HOVER = "#4a9a88"
SECONDARY = "#97d9ca"
ACCENT = "#71d8c1"
TEXT = "#1c2523"
MUTED = "#6d7a77"
DANGER = "#e07a5f"
DANGER_HOVER = "#cc6a51"
NEUTRAL = "#98a3a0"
NEUTRAL_HOVER = "#828f8c"

FONT_FAMILY = "Segoe UI"

# --- Configuration & State Persistence ---

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

app_config = load_config()
app_presets = app_config["presets"]

# --- Small UI Helpers ---

def add_hover(widget, hover_bg, normal_bg):
    """Swaps a button's background on mouse enter/leave, unless it's disabled."""
    def on_enter(_):
        if str(widget["state"]) != "disabled":
            widget.config(bg=hover_bg)
    def on_leave(_):
        if str(widget["state"]) != "disabled":
            widget.config(bg=normal_bg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def make_button(parent, text, command, bg=PRIMARY, hover=PRIMARY_HOVER, fg="white",
                 font=(FONT_FAMILY, 9, "bold"), padx=10, pady=6):
    btn = Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=padx,
        pady=pady,
        cursor="hand2",
        font=font,
    )
    add_hover(btn, hover, bg)
    return btn

def make_card(parent, bg=SURFACE):
    return Frame(parent, bg=bg, highlightbackground=BORDER, highlightthickness=1, bd=0)

class ToggleSwitch(Canvas):
    """A small iOS-style toggle switch bound to a BooleanVar."""

    def __init__(self, parent, variable, command=None, width=42, height=22,
                 on_color=PRIMARY, off_color="#c9d4d1", knob_color="#ffffff", bg=SURFACE):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, cursor="hand2")
        self.variable = variable
        self.command = command
        self.w = width
        self.h = height
        self.on_color = on_color
        self.off_color = off_color
        self.knob_color = knob_color
        self.bind("<Button-1>", self.toggle)
        self.redraw()

    def _rounded_pill(self, color):
        r = self.h / 2
        self.create_oval(0, 0, self.h, self.h, fill=color, outline=color)
        self.create_oval(self.w - self.h, 0, self.w, self.h, fill=color, outline=color)
        self.create_rectangle(r, 0, self.w - r, self.h, fill=color, outline=color)

    def redraw(self):
        self.delete("all")
        is_on = bool(self.variable.get())
        self._rounded_pill(self.on_color if is_on else self.off_color)
        pad = 3
        knob_d = self.h - pad * 2
        x0 = (self.w - knob_d - pad) if is_on else pad
        self.create_oval(x0, pad, x0 + knob_d, pad + knob_d, fill=self.knob_color, outline=self.knob_color)

    def set_bg(self, bg):
        self.config(bg=bg)
        self.redraw()

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self.redraw()
        if self.command:
            self.command()

def make_option_row(parent, icon, label_text, description, variable, command):
    """A clickable row with a label/description on the left and a toggle switch on the right."""
    row = Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
    inner = Frame(row, bg=SURFACE, padx=12, pady=9)
    inner.pack(fill="both", expand=True)

    text_box = Frame(inner, bg=SURFACE)
    text_box.pack(side=LEFT, fill="x", expand=True)

    title_lbl = Label(
        text_box, text=f"{icon}  {label_text}", font=(FONT_FAMILY, 9, "bold"),
        bg=SURFACE, fg=TEXT, anchor="w", justify="left"
    )
    title_lbl.pack(anchor="w")

    desc_lbl = None
    if description:
        desc_lbl = Label(
            text_box, text=description, font=(FONT_FAMILY, 8),
            bg=SURFACE, fg=MUTED, anchor="w", justify="left", wraplength=140
        )
        desc_lbl.pack(anchor="w", pady=(2, 0))

    switch = ToggleSwitch(inner, variable, command=command, bg=SURFACE)
    switch.pack(side=RIGHT, padx=(8, 0))

    hoverable = [row, inner, text_box, title_lbl] + ([desc_lbl] if desc_lbl else [])

    def on_click(event):
        if event.widget is not switch:
            switch.toggle()

    def on_enter(_):
        for w in hoverable:
            w.config(bg=CARD)
        switch.set_bg(CARD)

    def on_leave(_):
        for w in hoverable:
            w.config(bg=SURFACE)
        switch.set_bg(SURFACE)

    for w in hoverable:
        w.bind("<Button-1>", on_click)
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)

    return row

def center_fixed(win, parent, width, height):
    win.update_idletasks()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    x = px + (pw - width) // 2
    y = py + (ph - height) // 2
    win.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")

def center_auto(win, parent):
    win.update_idletasks()
    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    x = px + (pw - w) // 2
    y = py + (ph - h) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")

def _dialog_shell(parent, title):
    dialog = Toplevel(parent)
    dialog.title(title)
    dialog.config(bg=BG, padx=22, pady=18)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    return dialog

def custom_askstring(parent, title, prompt, initialvalue=""):
    """Styled replacement for tkinter.simpledialog.askstring."""
    result = {"value": None}
    dialog = _dialog_shell(parent, title)

    Label(
        dialog, text=prompt, font=(FONT_FAMILY, 10), bg=BG, fg=TEXT,
        wraplength=320, justify="left"
    ).pack(anchor="w", pady=(0, 10))

    entry_var = StringVar(value=initialvalue)
    entry = Entry(
        dialog, textvariable=entry_var, font=(FONT_FAMILY, 10),
        bg=SURFACE, fg=TEXT, relief="flat", insertbackground=TEXT,
        highlightbackground=BORDER, highlightcolor=PRIMARY, highlightthickness=1,
    )
    entry.pack(fill="x", ipady=6, pady=(0, 16))
    entry.focus_set()
    entry.select_range(0, END)

    btn_frame = Frame(dialog, bg=BG)
    btn_frame.pack(fill="x")

    def on_ok(event=None):
        result["value"] = entry_var.get()
        dialog.destroy()

    def on_cancel(event=None):
        dialog.destroy()

    make_button(btn_frame, "Cancel", on_cancel, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=14, pady=6).pack(side=RIGHT, padx=(8, 0))
    make_button(btn_frame, "OK", on_ok, padx=14, pady=6).pack(side=RIGHT)

    dialog.bind("<Return>", on_ok)
    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    center_auto(dialog, parent)
    parent.wait_window(dialog)
    return result["value"]

def custom_showinfo(parent, title, message, tone="warning"):
    """Styled replacement for tkinter.messagebox.showwarning/showinfo."""
    dialog = _dialog_shell(parent, title)
    color = DANGER if tone == "warning" else PRIMARY
    icon = "⚠" if tone == "warning" else "ℹ"

    Label(
        dialog, text=f"{icon}  {title}", font=(FONT_FAMILY, 12, "bold"),
        bg=BG, fg=color
    ).pack(anchor="w", pady=(0, 10))

    Label(
        dialog, text=message, font=(FONT_FAMILY, 9), bg=BG, fg=TEXT,
        wraplength=320, justify="left"
    ).pack(anchor="w", pady=(0, 16))

    def on_close(event=None):
        dialog.destroy()

    make_button(dialog, "OK", on_close, padx=14, pady=6).pack(fill="x")
    dialog.bind("<Return>", on_close)
    dialog.bind("<Escape>", on_close)
    dialog.protocol("WM_DELETE_WINDOW", on_close)

    center_auto(dialog, parent)
    parent.wait_window(dialog)

def custom_askyesno(parent, title, message, confirm_text="Delete", cancel_text="Cancel", danger=True):
    """Styled replacement for tkinter.messagebox.askyesno."""
    result = {"value": False}
    dialog = _dialog_shell(parent, title)
    color = DANGER if danger else PRIMARY
    icon = "⚠" if danger else "❓"

    Label(
        dialog, text=f"{icon}  {title}", font=(FONT_FAMILY, 12, "bold"),
        bg=BG, fg=color
    ).pack(anchor="w", pady=(0, 10))

    Label(
        dialog, text=message, font=(FONT_FAMILY, 9), bg=BG, fg=TEXT,
        wraplength=320, justify="left"
    ).pack(anchor="w", pady=(0, 16))

    btn_frame = Frame(dialog, bg=BG)
    btn_frame.pack(fill="x")

    def on_yes(event=None):
        result["value"] = True
        dialog.destroy()

    def on_no(event=None):
        dialog.destroy()

    make_button(btn_frame, confirm_text, on_yes, bg=color,
                hover=DANGER_HOVER if danger else PRIMARY_HOVER,
                padx=14, pady=6).pack(side=RIGHT, padx=(8, 0))
    make_button(btn_frame, cancel_text, on_no, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=14, pady=6).pack(side=RIGHT)

    dialog.bind("<Escape>", on_no)
    dialog.protocol("WM_DELETE_WINDOW", on_no)

    center_auto(dialog, parent)
    parent.wait_window(dialog)
    return result["value"]

def custom_resolve_conflicts(parent, category_name, conflicts):
    """Styled replacement for the extension-conflict messagebox.askyesnocancel.
    Returns True (reassign), False (keep originals), or None (cancel)."""
    result = {"value": None}
    dialog = _dialog_shell(parent, "Duplicate Extensions Detected")

    Label(
        dialog, text="⚠  Duplicate Extensions Detected", font=(FONT_FAMILY, 12, "bold"),
        bg=BG, fg=DANGER
    ).pack(anchor="w", pady=(0, 10))

    Label(
        dialog, text="The following extension(s) are already used in other categories:",
        font=(FONT_FAMILY, 9), bg=BG, fg=TEXT, wraplength=360, justify="left"
    ).pack(anchor="w", pady=(0, 8))

    conflict_list = Frame(dialog, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    conflict_list.pack(fill="x", pady=(0, 12))
    for ext, cat in conflicts.items():
        Label(
            conflict_list, text=f"•  {ext}   (currently in '{cat}')",
            font=(FONT_FAMILY, 9), bg=CARD, fg=TEXT, anchor="w"
        ).pack(fill="x", padx=10, pady=3)

    Label(
        dialog,
        text=f"Reassign moves them into '{category_name}'. Keep Original leaves them where they are.",
        font=(FONT_FAMILY, 8), bg=BG, fg=MUTED, wraplength=360, justify="left"
    ).pack(anchor="w", pady=(0, 14))

    btn_frame = Frame(dialog, bg=BG)
    btn_frame.pack(fill="x")

    def on_reassign(event=None):
        result["value"] = True
        dialog.destroy()

    def on_keep(event=None):
        result["value"] = False
        dialog.destroy()

    def on_cancel(event=None):
        dialog.destroy()

    make_button(btn_frame, "Reassign", on_reassign, padx=12, pady=6).pack(side=RIGHT, padx=(8, 0))
    make_button(btn_frame, "Keep Original", on_keep, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=12, pady=6).pack(side=RIGHT, padx=(8, 0))
    make_button(btn_frame, "Cancel", on_cancel, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=12, pady=6).pack(side=RIGHT)

    dialog.bind("<Escape>", on_cancel)
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    center_auto(dialog, parent)
    parent.wait_window(dialog)
    return result["value"]

# --- Main Application Window ---

window = Tk()
window.title("Desktop Declutter")
window.geometry("800x800")
window.config(padx=24, pady=20, bg=BG)
window.resizable(False, False)

# --- Application Icon ---

logo_path = os.path.join(script_dir, "Logo.png")

try:
    app_icon = PhotoImage(file=logo_path)
    window.iconphoto(True, app_icon)
except Exception as e:
    print(f"Could not load icon: {e}")

# --- Header Title ---

header_frame = Frame(window, bg=BG)
header_frame.pack(fill="x", pady=(0, 18))

lbl = Label(
    header_frame,
    text="Desktop Declutter",
    font=(FONT_FAMILY, 22, "bold"),
    bg=BG,
    fg=TEXT
)
lbl.pack(anchor="w")

subtitle_lbl = Label(
    header_frame,
    text="Sort a messy folder into tidy, categorized subfolders in one click.",
    font=(FONT_FAMILY, 10),
    bg=BG,
    fg=MUTED
)
subtitle_lbl.pack(anchor="w", pady=(2, 0))

# --- Folder & Preset Card ---

setup_card = make_card(window)
setup_card.pack(fill="x", pady=(0, 16))

setup_inner = Frame(setup_card, bg=SURFACE, padx=18, pady=16)
setup_inner.pack(fill="x")

folder_selected = "No folder was selected"

def choose_folder():
    global folder_selected
    folder_selected = filedialog.askdirectory(title="Select a Folder to Declutter")

    if folder_selected:
        path_label.config(text=folder_selected, fg=TEXT)
        log_message(f"Folder Selected: {folder_selected}")
    else:
        folder_selected = "No folder was selected"

row_frame = Frame(setup_inner, bg=SURFACE)
row_frame.pack(fill="x")

btn = make_button(row_frame, "📁  Select Folder", choose_folder)
btn.pack(side=LEFT, padx=(0, 15))

path_label = Label(
    row_frame,
    text="No folder selected",
    bg=SURFACE,
    fg=MUTED,
    font=(FONT_FAMILY, 9),
    wraplength=440,
    justify="left"
)
path_label.pack(side=LEFT, fill="x")

divider = Frame(setup_inner, bg=BORDER, height=1)
divider.pack(fill="x", pady=14)

# --- Preset Selection ---

preset_frame = Frame(setup_inner, bg=SURFACE)
preset_frame.pack(fill="x")

preset_label = Label(
    preset_frame,
    text="Sorting Preset",
    font=(FONT_FAMILY, 10, "bold"),
    bg=SURFACE,
    fg=TEXT
)
preset_label.pack(side=LEFT, padx=(0, 10))

current_preset_var = StringVar(value="Default")

style = Style()
style.theme_use("clam")

style.configure(
    "TCombobox",
    fieldbackground=SURFACE,
    background=SURFACE,
    foreground=TEXT,
    arrowcolor=PRIMARY,
    bordercolor=BORDER,
    lightcolor=SURFACE,
    darkcolor=SURFACE,
    padding=4,
)
style.map(
    "TCombobox",
    fieldbackground=[("readonly", SURFACE)],
    background=[("readonly", SURFACE)],
)

preset_dropdown = Combobox(
    preset_frame,
    textvariable=current_preset_var,
    values=list(app_presets.keys()),
    state="readonly",
    font=(FONT_FAMILY, 10),
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
    modal.config(padx=20, pady=20, bg=BG)
    modal.resizable(False, False)
    modal.transient(parent)
    modal.grab_set()
    center_fixed(modal, parent, 540, 460)

    header_frame = Frame(modal, bg=BG)
    header_frame.pack(fill="x", pady=(0, 15))

    Label(
        header_frame,
        text="Manage Presets",
        font=(FONT_FAMILY, 16, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(side=LEFT)

    def add_new_preset():
        new_name = custom_askstring(modal, "New Preset", "Enter a name for the new preset:")
        if new_name and new_name.strip():
            name = new_name.strip()
            if name in app_presets:
                custom_showinfo(modal, "Preset Exists", "A preset with this name already exists.")
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

    make_button(header_frame, "+ New Preset", add_new_preset, padx=10, pady=4,
                font=(FONT_FAMILY, 9, "bold")).pack(side=RIGHT)

    list_container = Frame(modal, bg=BG)
    list_container.pack(fill="both", expand=True, pady=(0, 15))

    def refresh_preset_rows():
        for widget in list_container.winfo_children():
            widget.destroy()

        for name in app_presets.keys():
            render_preset_row(name, is_default=(name == "Default"))

    def render_preset_row(name, is_default=False):
        row = Frame(list_container, bg=CARD, highlightbackground=BORDER, highlightthickness=1, padx=12, pady=10)
        row.pack(fill="x", pady=4)

        Label(
            row,
            text=name,
            font=(FONT_FAMILY, 10, "bold"),
            bg=CARD,
            fg=TEXT
        ).pack(side=LEFT)

        def delete_preset(target_name):
            if custom_askyesno(modal, "Delete Preset", f"Delete preset '{target_name}'? This cannot be undone."):
                del app_presets[target_name]
                save_config(app_config)
                preset_dropdown["values"] = list(app_presets.keys())
                if current_preset_var.get() == target_name:
                    current_preset_var.set("Default")
                refresh_preset_rows()

        if not is_default:
            make_button(row, "Delete", lambda n=name: delete_preset(n), bg=DANGER, hover=DANGER_HOVER,
                        padx=8, pady=2, font=(FONT_FAMILY, 9)).pack(side=RIGHT, padx=(6, 0))

        make_button(row, "Edit Categories", lambda n=name: open_manage_categories(n),
                    padx=8, pady=2, font=(FONT_FAMILY, 9)).pack(side=RIGHT)

    refresh_preset_rows()

    make_button(modal, "Close", modal.destroy, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=15, pady=8).pack(side=BOTTOM, fill="x")

manage_btn = make_button(preset_frame, "⚙  Manage Presets", open_manage_presets,
                          padx=10, pady=5, font=(FONT_FAMILY, 9, "bold"))
manage_btn.pack(side=RIGHT)

# --- Category & Extension Editor ---

def open_manage_categories(preset_name="Default"):
    open_categories_manager_modal(window, preset_name)

def open_categories_manager_modal(parent, preset_name):
    modal = Toplevel(parent)
    modal.title(f"Edit Preset - {preset_name}")
    modal.config(padx=20, pady=20, bg=BG)
    modal.resizable(False, False)
    modal.transient(parent)
    modal.grab_set()
    center_fixed(modal, parent, 580, 520)

    header_frame = Frame(modal, bg=BG)
    header_frame.pack(fill="x", pady=(0, 10))

    title_box = Frame(header_frame, bg=BG)
    title_box.pack(side=LEFT)

    Label(
        title_box,
        text=f"Editing: {preset_name}",
        font=(FONT_FAMILY, 15, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(anchor="w")

    Label(
        title_box,
        text="Manage target folders and assigned extensions",
        font=(FONT_FAMILY, 9),
        bg=BG,
        fg=MUTED
    ).pack(anchor="w")

    def add_new_category():
        cat_name = custom_askstring(modal, "New Directory", "Enter folder name (e.g., Spreadsheets):")
        if cat_name and cat_name.strip():
            cat = cat_name.strip()
            preset_cats = app_presets[preset_name]["categories"]
            if cat in preset_cats:
                custom_showinfo(modal, "Folder Exists", "A folder with this name already exists in this preset.")
                return
            preset_cats[cat] = []
            save_config(app_config)
            refresh_categories()

    make_button(header_frame, "+ Add Directory", add_new_category, padx=10, pady=4,
                font=(FONT_FAMILY, 9, "bold")).pack(side=RIGHT)

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
        user_input = custom_askstring(
            modal,
            f"Edit Extensions - {category_name}",
            f"Enter comma-separated extensions for {category_name}:\n(e.g., .png, .jpg, .svg)",
            initialvalue=curr_exts,
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

        all_categories = app_presets[preset_name]["categories"]
        conflicts = {}

        for ext in new_exts:
            for other_cat, exts_list in all_categories.items():
                if other_cat != category_name and ext in exts_list:
                    conflicts[ext] = other_cat

        if conflicts:
            reassign = custom_resolve_conflicts(modal, category_name, conflicts)

            if reassign is None:
                return

            if reassign:
                for ext, other_cat in conflicts.items():
                    if ext in all_categories[other_cat]:
                        all_categories[other_cat].remove(ext)
            else:
                new_exts = [ext for ext in new_exts if ext not in conflicts]

        app_presets[preset_name]["categories"][category_name] = new_exts
        save_config(app_config)
        refresh_categories()

    def delete_category(category_name):
        if custom_askyesno(modal, "Delete Directory", f"Remove folder category '{category_name}'? Files already sorted there will remain."):
            del app_presets[preset_name]["categories"][category_name]
            save_config(app_config)
            refresh_categories()

    def render_category_row(cat_name, extensions):
        row = Frame(cat_list_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1, padx=12, pady=8)
        row.pack(fill="x", pady=3)

        info_box = Frame(row, bg=CARD)
        info_box.pack(side=LEFT, fill="x", expand=True)

        Label(
            info_box,
            text=cat_name,
            font=(FONT_FAMILY, 10, "bold"),
            bg=CARD,
            fg=TEXT
        ).pack(anchor="w")

        ext_preview = ", ".join(extensions) if extensions else "No extensions assigned"
        Label(
            info_box,
            text=ext_preview,
            font=(FONT_FAMILY, 8),
            bg=CARD,
            fg=MUTED,
            wraplength=280,
            justify="left"
        ).pack(anchor="w")

        make_button(row, "Delete", lambda c=cat_name: delete_category(c), bg=DANGER, hover=DANGER_HOVER,
                    padx=8, pady=2, font=(FONT_FAMILY, 9)).pack(side=RIGHT, padx=(6, 0))

        make_button(row, "Edit Extensions", lambda c=cat_name: edit_extensions(c),
                    padx=8, pady=2, font=(FONT_FAMILY, 9)).pack(side=RIGHT)

    refresh_categories()

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
        font=(FONT_FAMILY, 9),
        cursor="hand2"
    )
    other_check.pack(anchor="w", pady=(0, 15))

    make_button(modal, "Done", modal.destroy, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=15, pady=8).pack(side=BOTTOM, fill="x")

# --- Deletion Confirmation Warning Modal ---

def confirm_deletion_action():
    if app_config.get("settings", {}).get("never_show_again_delete_prompt", False):
        return True

    confirmed = False
    prompt = Toplevel(window)
    prompt.title("Warning: Permanent Action")
    prompt.config(padx=20, pady=15, bg=BG)
    prompt.resizable(False, False)
    prompt.transient(window)
    prompt.grab_set()
    center_fixed(prompt, window, 450, 230)

    Label(
        prompt,
        text="⚠️ Warning: Permanent File Deletion",
        font=(FONT_FAMILY, 13, "bold"),
        bg=BG,
        fg=DANGER
    ).pack(anchor="w", pady=(0, 10))

    warning_text = (
        "You have enabled features that permanently delete files or folders "
        "(e.g., Duplicates or Empty Folders). These operations cannot be undone.\n\n"
        "Do you want to proceed?"
    )
    Label(
        prompt,
        text=warning_text,
        font=(FONT_FAMILY, 9),
        bg=BG,
        fg=TEXT,
        wraplength=410,
        justify="left"
    ).pack(anchor="w", pady=(0, 10))

    never_show_var = BooleanVar(value=False)
    Checkbutton(
        prompt,
        text="Don't show this prompt in the future",
        variable=never_show_var,
        bg=BG,
        fg=TEXT,
        activebackground=BG,
        selectcolor="white",
        font=(FONT_FAMILY, 9),
        cursor="hand2"
    ).pack(anchor="w", pady=(0, 15))

    btn_frame = Frame(prompt, bg=BG)
    btn_frame.pack(fill="x")

    def on_continue():
        nonlocal confirmed
        confirmed = True
        if never_show_var.get():
            if "settings" not in app_config:
                app_config["settings"] = {}
            app_config["settings"]["never_show_again_delete_prompt"] = True
            save_config(app_config)
        prompt.destroy()

    def on_cancel():
        prompt.destroy()

    make_button(btn_frame, "Continue", on_continue, bg=DANGER, hover=DANGER_HOVER,
                padx=14, pady=5, font=(FONT_FAMILY, 9, "bold")).pack(side=RIGHT, padx=(8, 0))

    make_button(btn_frame, "Cancel", on_cancel, bg=NEUTRAL, hover=NEUTRAL_HOVER,
                padx=14, pady=5, font=(FONT_FAMILY, 9)).pack(side=RIGHT)

    window.wait_window(prompt)
    return confirmed

# --- Scan Execution ---

last_moved_history = []

def start_declutter():
    if folder_selected == "No folder was selected":
        log_message("Please select a folder first!")
        return

    has_delete_action = (
        delete_duplicates_var.get() or
        delete_empty_var.get() or
        delete_only_var.get()
    )

    if has_delete_action:
        if not confirm_deletion_action():
            log_message("Operation cancelled by user.")
            return

    start_btn.config(state="disabled")
    progress_bar["value"] = 0
    progress_label.config(text="")

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

        start_btn.config(state="normal")

        if last_moved_history:
            undo_btn.config(state="normal", bg=NEUTRAL_HOVER, cursor="hand2")

    threading.Thread(target=run_scan, daemon=True).start()

action_row = Frame(window, bg=BG)
action_row.pack(fill="x", pady=(4, 12))

start_btn = make_button(
    action_row,
    "▶  Start Scan",
    start_declutter,
    bg=PRIMARY,
    hover=PRIMARY_HOVER,
    font=(FONT_FAMILY, 12, "bold"),
    padx=20,
    pady=10,
)
start_btn.pack(side=LEFT, fill="x", expand=True, padx=(0, 6))

# --- Undo Execution ---

def undo_declutter():
    global last_moved_history

    if not last_moved_history:
        return

    start_btn.config(state="disabled")
    undo_btn.config(state="disabled", bg=NEUTRAL, cursor="arrow")
    progress_bar["value"] = 0
    progress_label.config(text="")

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

undo_btn = make_button(
    action_row,
    "↺  Undo Sort",
    undo_declutter,
    bg=NEUTRAL,
    hover=NEUTRAL_HOVER,
    font=(FONT_FAMILY, 12, "bold"),
    padx=20,
    pady=10,
)
undo_btn.config(state="disabled", cursor="arrow")
undo_btn.pack(side=LEFT, fill="x", expand=True, padx=(6, 0))

# --- Progress Bar ---

def update_progress(current_item: int, total_items: int):
    progress_bar["maximum"] = total_items
    progress_bar["value"] = current_item
    if total_items:
        percent = int((current_item / total_items) * 100)
        progress_label.config(text=f"{current_item}/{total_items}  ({percent}%)")

progress_row = Frame(window, bg=BG)
progress_row.pack(fill="x", pady=(0, 4))

progress_label = Label(progress_row, text="", bg=BG, fg=MUTED, font=(FONT_FAMILY, 8))
progress_label.pack(side=RIGHT)

style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor=CARD,
    background=ACCENT,
    bordercolor=CARD,
    lightcolor=ACCENT,
    darkcolor=ACCENT,
)

progress_bar = Progressbar(
    window,
    orient="horizontal",
    mode="determinate",
    style="Custom.Horizontal.TProgressbar"
)
progress_bar.pack(fill="x", pady=(0, 14))

# --- Bottom Frame Container ---

bottom_frame = Frame(window, bg=BG)
bottom_frame.pack(fill="both", expand=True)

# --- Options Sidebar ---

options_card = make_card(bottom_frame)
options_card.pack(side=LEFT, fill="y", padx=(0, 16))

options_frame = Frame(options_card, bg=SURFACE, padx=16, pady=14)
options_frame.pack(fill="both", expand=True)

options_label = Label(
    options_frame,
    text="Options",
    font=(FONT_FAMILY, 13, "bold"),
    bg=SURFACE,
    fg=TEXT,
)
options_label.pack(anchor="w", pady=(0, 4))

options_sub = Label(
    options_frame,
    text="Toggle extra scan behavior",
    font=(FONT_FAMILY, 8),
    bg=SURFACE,
    fg=MUTED,
)
options_sub.pack(anchor="w", pady=(0, 14))

# --- Option: Delete Only Mode ---

delete_only_var = BooleanVar(value=False)

def on_toggle():
    log_message(f"Delete only mode was set to: {delete_only_var.get()}")

delete_only_row = make_option_row(
    options_frame, "🗑", "Delete Only Mode", "Skip sorting, only run delete actions",
    delete_only_var, on_toggle
)
delete_only_row.pack(side=TOP, fill="x", pady=(0, 8))

# --- Option: Delete Empty Folders ---

delete_empty_var = BooleanVar(value=False)

def on_toggle_empty():
    log_message(f"Delete empty folders was set to: {delete_empty_var.get()}")

delete_empty_row = make_option_row(
    options_frame, "📂", "Delete Empty Folders", "Remove empty folders after sorting",
    delete_empty_var, on_toggle_empty
)
delete_empty_row.pack(side=TOP, fill="x", pady=(0, 8))

# --- Option: Delete Duplicates ---

delete_duplicates_var = BooleanVar(value=False)

def on_toggle_duplicates():
    log_message(f"Delete duplicates was set to: {delete_duplicates_var.get()}")

delete_duplicates_row = make_option_row(
    options_frame, "🧬", "Delete Duplicates", "Delete duplicate files by content",
    delete_duplicates_var, on_toggle_duplicates
)
delete_duplicates_row.pack(side=TOP, fill="x", pady=(0, 8))

warning_note = Label(
    options_frame,
    text="⚠ Delete actions are permanent.",
    font=(FONT_FAMILY, 8),
    bg=SURFACE,
    fg=DANGER,
    wraplength=170,
    justify="left",
)
warning_note.pack(side=TOP, anchor="w", pady=(6, 0))

# --- Action Console Log ---

log_card = make_card(bottom_frame)
log_card.pack(side=LEFT, fill="both", expand=True)

log_inner = Frame(log_card, bg=SURFACE, padx=14, pady=12)
log_inner.pack(fill="both", expand=True)

log_header = Label(
    log_inner,
    text="Activity Log",
    font=(FONT_FAMILY, 13, "bold"),
    bg=SURFACE,
    fg=TEXT,
)
log_header.pack(anchor="w", pady=(0, 8))

msg_box = scrolledtext.ScrolledText(
    log_inner,
    width=50,
    height=8,
    font=("Consolas", 9),
    bg=CARD,
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    bd=0,
    padx=10,
    pady=8,
    highlightbackground=BORDER,
    highlightthickness=1,
    state="disabled"
)
msg_box.pack(fill="both", expand=True)

def log_message(message: str):
    msg_box.config(state="normal")
    msg_box.insert(END, message + "\n")
    msg_box.see(END)
    msg_box.config(state="disabled")

log_message("Select a folder to get started")

# --- Event Loop ---

window.mainloop()
