"""
Py2Win GUI - A user-friendly graphical interface for PyInstaller.

This application provides a complete GUI for the features of PyInstaller,
allowing users to easily package their Python scripts into standalone
Windows executables.

Features:
- A simple, clean, dark-themed interface built with customtkinter.
- Basic options: console/windowed app, one-file/one-dir build.
- Pro features: custom icon selection, bundling of additional data files and folders.
- Real-time logging of the PyInstaller build process.
- Responsive UI that doesn't freeze during builds, thanks to multi-threading.

Usage:
  python py2win_gui.py

Dependencies:
- customtkinter
- pyinstaller
"""
import customtkinter as ctk
from tkinter import filedialog, Listbox
import threading
import subprocess
import queue
import os
import json
import shutil


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.tooltip_window, text=self.text, corner_radius=5, fg_color="#363636", wraplength=200)
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None


class Py2WinApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Py2Win")
        self.geometry("800x650")
        self.minsize(600, 500)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- UI Elements ---
        self.create_widgets()
        self.update_status("Ready")
        self.check_dependencies()

    def check_dependencies(self):
        if not shutil.which("pyinstaller"):
            self.log("ERROR: PyInstaller is not installed or not in your system's PATH.")
            self.log("Please install it using: pip install pyinstaller")
            self.update_status("Error: PyInstaller not found!")
            self.build_button.configure(state="disabled", text="PyInstaller Not Found")

    def show_about_window(self):
        about_win = ctk.CTkToplevel(self)
        about_win.title("About Py2Win")
        about_win.geometry("400x250")
        about_win.transient(self) # Keep on top of the main window
        about_win.grab_set() # Modal

        about_win.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(about_win, text="Py2Win GUI", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        version_label = ctk.CTkLabel(about_win, text="Version 1.0.0")
        version_label.grid(row=1, column=0, padx=20, pady=0)

        desc_label = ctk.CTkLabel(about_win, text="A user-friendly graphical interface for PyInstaller.", wraplength=360)
        desc_label.grid(row=2, column=0, padx=20, pady=10)

        credit_label = ctk.CTkLabel(about_win, text="Packaged with assistance from Jules.")
        credit_label.grid(row=3, column=0, padx=20, pady=10)

        ok_button = ctk.CTkButton(about_win, text="OK", command=about_win.destroy)
        ok_button.grid(row=4, column=0, padx=20, pady=(20,20))

    def create_widgets(self):
        # --- Profile Management Frame ---
        self.profile_frame = ctk.CTkFrame(self)
        self.profile_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.profile_frame.grid_columnconfigure(1, weight=1)

        self.about_button = ctk.CTkButton(self.profile_frame, text="About", command=self.show_about_window, width=80)
        self.about_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.load_profile_button = ctk.CTkButton(self.profile_frame, text="Load Profile", command=self.load_profile)
        self.load_profile_button.grid(row=0, column=3, padx=10, pady=10, sticky="e")

        self.save_profile_button = ctk.CTkButton(self.profile_frame, text="Save Profile", command=self.save_profile)
        self.save_profile_button.grid(row=0, column=2, padx=(10,5), pady=10, sticky="e")

        # --- Script Selection Frame ---
        self.script_frame = ctk.CTkFrame(self)
        self.script_frame.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="ew")
        self.script_frame.grid_columnconfigure(1, weight=1)
        self.script_label = ctk.CTkLabel(self.script_frame, text="Python Script:")
        self.script_label.grid(row=0, column=0, padx=10, pady=10)
        self.script_entry = ctk.CTkEntry(self.script_frame, placeholder_text="Select your main .py script")
        self.script_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(self.script_frame, text="Browse", command=self.browse_script)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Tab View for Options ---
        self.tab_view = ctk.CTkTabview(self, corner_radius=8)
        self.tab_view.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.tab_view.add("Basic Options")
        self.tab_view.add("Pro Features")

        # --- Basic Options Tab ---
        self.basic_tab = self.tab_view.tab("Basic Options")
        self.windowed_check = ctk.CTkCheckBox(self.basic_tab, text="Windowed App (No Console)")
        self.windowed_check.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        Tooltip(self.windowed_check, "Enable this for GUI applications. A command prompt window will not appear.")

        self.onefile_check = ctk.CTkCheckBox(self.basic_tab, text="One-File Executable")
        self.onefile_check.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.onefile_check.select()
        Tooltip(self.onefile_check, "Package everything into a single executable file. Startup may be slower.")

        # --- Pro Features Tab ---
        self.pro_tab = self.tab_view.tab("Pro Features")
        self.pro_tab.grid_columnconfigure(0, weight=1)
        self.pro_tab.grid_rowconfigure(1, weight=1)
        
        self.icon_frame = ctk.CTkFrame(self.pro_tab)
        self.icon_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.icon_frame.grid_columnconfigure(1, weight=1)
        self.icon_label = ctk.CTkLabel(self.icon_frame, text="Custom Icon:")
        self.icon_label.grid(row=0, column=0, padx=10, pady=10)
        self.icon_entry = ctk.CTkEntry(self.icon_frame, placeholder_text="Select a .ico file")
        self.icon_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.icon_browse_button = ctk.CTkButton(self.icon_frame, text="Browse", command=self.browse_icon)
        self.icon_browse_button.grid(row=0, column=2, padx=10, pady=10)
        Tooltip(self.icon_browse_button, "Select a .ico file to use as the icon for the executable.")

        self.data_frame = ctk.CTkFrame(self.pro_tab)
        self.data_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.data_frame.grid_columnconfigure(0, weight=1)
        self.data_frame.grid_rowconfigure(1, weight=1)
        self.data_label = ctk.CTkLabel(self.data_frame, text="Additional Files & Folders:")
        self.data_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        self.data_listbox = Listbox(self.data_frame, bg="#2B2B2B", fg="white", selectbackground="#1F6AA5", borderwidth=0, highlightthickness=1, highlightcolor="#565B5E", selectmode="extended")
        self.data_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.data_paths = []
        self.data_buttons_frame = ctk.CTkFrame(self.data_frame)
        self.data_buttons_frame.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ns")
        self.add_file_button = ctk.CTkButton(self.data_buttons_frame, text="Add File(s)", command=self.add_data_file)
        self.add_file_button.grid(row=0, column=0, padx=5, pady=5)
        Tooltip(self.add_file_button, "Bundle additional data files with your executable (e.g., images, configs).")

        self.add_folder_button = ctk.CTkButton(self.data_buttons_frame, text="Add Folder", command=self.add_data_folder)
        self.add_folder_button.grid(row=1, column=0, padx=5, pady=5)
        Tooltip(self.add_folder_button, "Bundle an entire folder and its contents.")

        self.remove_data_button = ctk.CTkButton(self.data_buttons_frame, text="Remove", command=self.remove_selected_data)
        self.remove_data_button.grid(row=2, column=0, padx=5, pady=5)

        # --- Output Textbox ---
        self.output_textbox = ctk.CTkTextbox(self, state="disabled", corner_radius=8)
        self.output_textbox.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="nsew")

        # --- Build Button ---
        self.build_button = ctk.CTkButton(self, text="Build Executable", height=40, command=self.start_build_thread)
        self.build_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="", anchor="w")
        self.status_bar.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")

    def save_profile(self):
        self.update_status("Saving profile...")
        profile_path = filedialog.asksaveasfilename(
            title="Save Build Profile",
            defaultextension=".json",
            filetypes=(("Py2Win Profiles", "*.json"), ("All files", "*.*"))
        )
        if not profile_path:
            self.update_status("Save cancelled.")
            return

        settings = {
            "script_path": self.script_entry.get(),
            "is_windowed": self.windowed_check.get(),
            "is_onefile": self.onefile_check.get(),
            "icon_path": self.icon_entry.get(),
            "data_paths": list(self.data_paths)
        }

        try:
            with open(profile_path, 'w') as f:
                json.dump(settings, f, indent=4)
            self.update_status(f"Profile saved to {os.path.basename(profile_path)}")
        except Exception as e:
            self.update_status(f"Error saving profile: {e}")
            self.log(f"Error saving profile: {e}")

    def load_profile(self):
        self.update_status("Loading profile...")
        profile_path = filedialog.askopenfilename(
            title="Load Build Profile",
            filetypes=(("Py2Win Profiles", "*.json"), ("All files", "*.*"))
        )
        if not profile_path:
            self.update_status("Load cancelled.")
            return

        try:
            with open(profile_path, 'r') as f:
                settings = json.load(f)

            # Clear existing settings
            self.script_entry.delete(0, "end")
            self.icon_entry.delete(0, "end")
            self.data_listbox.delete(0, "end")
            self.data_paths.clear()

            # Apply loaded settings
            self.script_entry.insert(0, settings.get("script_path", ""))
            self.icon_entry.insert(0, settings.get("icon_path", ""))

            if settings.get("is_windowed", 0): self.windowed_check.select()
            else: self.windowed_check.deselect()

            if settings.get("is_onefile", 1): self.onefile_check.select()
            else: self.onefile_check.deselect()

            for path in settings.get("data_paths", []):
                self.data_paths.append(path)
                prefix = "DIR:  " if os.path.isdir(path) else "FILE: "
                self.data_listbox.insert("end", f"{prefix}{path}")

            self.update_status(f"Profile loaded from {os.path.basename(profile_path)}")

        except (json.JSONDecodeError, KeyError) as e:
            self.update_status(f"Error: Invalid or corrupt profile file.")
            self.log(f"Error loading profile: {e}")
        except Exception as e:
            self.update_status(f"Error loading profile: {e}")
            self.log(f"Error loading profile: {e}")

    def browse_script(self):
        self.update_status("Browsing for Python script...")
        filepath = filedialog.askopenfilename(title="Select a Python Script", filetypes=(("Python files", "*.py *.pyw"), ("All files", "*.*")))
        if filepath:
            self.script_entry.delete(0, "end")
            self.script_entry.insert(0, filepath)
            self.update_status(f"Selected script: {os.path.basename(filepath)}")
        else:
            self.update_status("Ready")

    def browse_icon(self):
        self.update_status("Browsing for icon file...")
        filepath = filedialog.askopenfilename(title="Select an Icon File", filetypes=(("Icon files", "*.ico"), ("All files", "*.*")))
        if filepath:
            self.icon_entry.delete(0, "end")
            self.icon_entry.insert(0, filepath)
            self.update_status(f"Selected icon: {os.path.basename(filepath)}")
        else:
            self.update_status("Ready")

    def add_data_file(self):
        filepaths = filedialog.askopenfilenames(title="Select File(s) to Bundle")
        if filepaths:
            for path in filepaths:
                if path not in self.data_paths:
                    self.data_paths.append(path)
                    self.data_listbox.insert("end", f"FILE: {path}")
            self.update_status(f"Added {len(filepaths)} file(s).")

    def add_data_folder(self):
        folderpath = filedialog.askdirectory(title="Select a Folder to Bundle")
        if folderpath and folderpath not in self.data_paths:
            self.data_paths.append(folderpath)
            self.data_listbox.insert("end", f"DIR:  {folderpath}")
            self.update_status(f"Added folder: {os.path.basename(folderpath)}")

    def remove_selected_data(self):
        selected_indices = self.data_listbox.curselection()
        if not selected_indices:
            return
        for i in sorted(selected_indices, reverse=True):
            self.data_listbox.delete(i)
            del self.data_paths[i]
        self.update_status(f"Removed {len(selected_indices)} item(s).")

    def log(self, message):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def update_status(self, message):
        self.status_bar.configure(text=message)

    def update_output_log(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line is None: # Sentinel value
                    if self.build_successful:
                        self.update_status("Build successful!")
                    else:
                        self.update_status("Build failed. Check log for details.")
                    self.build_button.configure(state="normal", text="Build Executable")
                    return
                self.log(line.strip())
        except queue.Empty:
            pass
        if self.build_button.cget("state") == "disabled":
            self.after(100, self.update_output_log)

    def start_build_thread(self):
        script_path = self.script_entry.get()
        if not script_path or not os.path.exists(script_path):
            self.update_status("Error: Please select a valid Python script.")
            self.log("Error: Please select a valid Python script.")
            return

        self.build_button.configure(state="disabled", text="Building...")
        self.update_status("Building... See log for details.")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")
        
        self.output_queue = queue.Queue()
        self.build_successful = False
        
        build_thread = threading.Thread(target=self.run_build_process, args=(script_path,), daemon=True)
        build_thread.start()
        self.after(100, self.update_output_log)

    def run_build_process(self, script_path):
        icon_path = self.icon_entry.get()
        additional_files = list(self.data_paths)
        is_windowed = self.windowed_check.get()
        is_onefile = self.onefile_check.get()

        command = ["pyinstaller", "--clean"]
        if is_onefile: command.append("--onefile")
        if is_windowed: command.append("--windowed")
        if icon_path and os.path.exists(icon_path): command.append(f"--icon={icon_path}")
        for path in additional_files:
            source_path = os.path.abspath(path)
            if os.path.exists(source_path):
                destination = os.path.basename(source_path) if os.path.isdir(source_path) else "."
                separator = ";" if os.name == 'nt' else ":"
                command.append(f'--add-data={source_path}{separator}{destination}')
        command.append(script_path)

        self.output_queue.put(f"Running command: {' '.join(command)}\n")
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(process.stdout.readline, ''):
                self.output_queue.put(line)
            process.stdout.close()
            process.wait()
            if process.returncode == 0:
                self.output_queue.put("\n--- Build successful! ---")
                self.build_successful = True
            else:
                self.output_queue.put(f"\n--- Build failed with exit code {process.returncode} ---")
        except Exception as e:
            self.output_queue.put(f"\n--- An unexpected error occurred: {e} ---")
        finally:
            self.output_queue.put(None)

if __name__ == "__main__":
    app = Py2WinApp()
    app.mainloop()
