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

class Py2WinApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Py2Win")
        self.geometry("800x650")
        self.minsize(600, 500)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- UI Elements ---
        self.create_widgets()
        self.update_status("Ready")

    def create_widgets(self):
        # --- Script Selection Frame ---
        self.script_frame = ctk.CTkFrame(self)
        self.script_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.script_frame.grid_columnconfigure(1, weight=1)
        self.script_label = ctk.CTkLabel(self.script_frame, text="Python Script:")
        self.script_label.grid(row=0, column=0, padx=10, pady=10)
        self.script_entry = ctk.CTkEntry(self.script_frame, placeholder_text="Select your main .py script")
        self.script_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(self.script_frame, text="Browse", command=self.browse_script)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Tab View for Options ---
        self.tab_view = ctk.CTkTabview(self, corner_radius=8)
        self.tab_view.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.tab_view.add("Basic Options")
        self.tab_view.add("Pro Features")

        # --- Basic Options Tab ---
        self.basic_tab = self.tab_view.tab("Basic Options")
        self.windowed_check = ctk.CTkCheckBox(self.basic_tab, text="Windowed App (No Console)")
        self.windowed_check.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.onefile_check = ctk.CTkCheckBox(self.basic_tab, text="One-File Executable")
        self.onefile_check.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.onefile_check.select()

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
        self.add_folder_button = ctk.CTkButton(self.data_buttons_frame, text="Add Folder", command=self.add_data_folder)
        self.add_folder_button.grid(row=1, column=0, padx=5, pady=5)
        self.remove_data_button = ctk.CTkButton(self.data_buttons_frame, text="Remove", command=self.remove_selected_data)
        self.remove_data_button.grid(row=2, column=0, padx=5, pady=5)

        # --- Output Textbox ---
        self.output_textbox = ctk.CTkTextbox(self, state="disabled", corner_radius=8)
        self.output_textbox.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")

        # --- Build Button ---
        self.build_button = ctk.CTkButton(self, text="Build Executable", height=40, command=self.start_build_thread)
        self.build_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="", anchor="w")
        self.status_bar.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

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
