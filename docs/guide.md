# Py2Win GUI User Guide

Welcome to Py2Win GUI, a user-friendly tool to help you package your Python scripts into standalone Windows executables.

## Main Features

- **Simple Interface:** All options are clearly laid out in a clean, tabbed interface.
- **Profile Management:** Save and load your build configurations to quickly switch between projects.
- **PyInstaller Options:** Supports basic and advanced PyInstaller features like:
    - One-File or One-Folder builds.
    - Console or Windowed (GUI) applications.
    - Custom icons for your executable.
    - Bundling additional data files and folders.
- **Real-time Logging:** See the output from PyInstaller as it builds your application.

## How to Use

### 1. Basic Build

1.  **Select your script:** Click the "Browse" button at the top to select your main Python (`.py` or `.pyw`) file.
2.  **Choose your options:**
    - **Windowed App:** Check this if you are building a GUI application (e.g., using Tkinter, PyQt, CustomTkinter). Leave it unchecked for console scripts.
    - **One-File Executable:** Check this to get a single `.exe` file. This is convenient but may have a slightly slower startup time.
3.  **Click "Build Executable".**
4.  The output from PyInstaller will appear in the log window.
5.  Once the build is successful, you will find your executable in a `dist` folder inside the directory where your script is located.

### 2. Using Profiles

If you work on multiple projects or have complex build configurations, profiles are very useful.

- **To Save a Profile:**
    1.  Set up your build configuration (select script, icon, add data files, etc.).
    2.  Click the **"Save Profile"** button.
    3.  Choose a name and location for your `.json` profile file.

- **To Load a Profile:**
    1.  Click the **"Load Profile"** button.
    2.  Select a previously saved `.json` profile file.
    3.  All the settings will be automatically loaded into the GUI.

### 3. Pro Features

- **Custom Icon:** Click "Browse" in the "Pro Features" tab to select a `.ico` file to use as the icon for your executable.
- **Additional Files & Folders:**
    - Use the **"Add File(s)"** and **"Add Folder"** buttons to select any other assets your script needs to run (e.g., images, configuration files, databases).
    - These files will be bundled with your application and will be available at runtime.
    - To remove an item from the list, select it and click **"Remove"**.

## Dependencies

Before building, make sure you have `pyinstaller` installed in your Python environment. If it is not found, the application will show a warning. You can install it with:
```
pip install pyinstaller
```
