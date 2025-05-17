import os
import subprocess
import sys
import shutil

def build_exe():
    """Build the executable using PyInstaller."""
    print("Building PF2E Autobattler executable...")
    
    # Ensure we have all requirements installed
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create dist and build directories if they don't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Build the executable
    print("Building executable...")
    subprocess.check_call([
        "pyinstaller",
        "--clean",
        "pf2e_autobattler.spec"
    ])
    
    # Create a zip file of the dist folder
    print("Creating distribution zip...")
    if os.path.exists('dist/PF2E_Autobattler'):
        shutil.make_archive('dist/PF2E_Autobattler', 'zip', 'dist/PF2E_Autobattler')
    
    print("\nBuild complete!")
    print("You can find the executable in the 'dist/PF2E_Autobattler' directory")
    print("A zip file has also been created at 'dist/PF2E_Autobattler.zip'")

if __name__ == "__main__":
    build_exe() 