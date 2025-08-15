import subprocess
import os
import shutil

# --- Configuration ---
APP_NAME = "Py2Win"
SCRIPT_PATH = os.path.join("src", "py2win_gui.py")
ICON_PATH = os.path.join("assets", "icon.ico")
ASSETS_PATH = "assets"
DIST_PATH = "dist"
BUILD_PATH = "build"

def main():
    print("--- Starting build process ---")

    # Clean up previous builds
    print("Cleaning up previous build directories...")
    if os.path.exists(DIST_PATH):
        shutil.rmtree(DIST_PATH)
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)

    # Construct the PyInstaller command
    command = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        f"--icon={ICON_PATH}",
        f"--add-data={ASSETS_PATH}{os.pathsep}assets",
        "--distpath", DIST_PATH,
        "--workpath", BUILD_PATH,
        "--specpath", ".", # Place the .spec file in the root
        SCRIPT_PATH
    ]

    print(f"Running command: {' '.join(command)}")

    # Run the command
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            print("\n--- Build successful! ---")
            print(f"Executable created in: {os.path.abspath(DIST_PATH)}")
        else:
            print(f"\n--- Build failed with exit code {process.returncode} ---")

    except FileNotFoundError:
        print("\n--- ERROR: pyinstaller command not found. ---")
        print("Please make sure PyInstaller is installed and in your system's PATH.")
        print("Install it with: pip install pyinstaller")
    except Exception as e:
        print(f"\n--- An unexpected error occurred: {e} ---")

if __name__ == "__main__":
    main()
