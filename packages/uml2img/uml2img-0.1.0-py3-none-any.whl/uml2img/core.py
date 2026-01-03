import subprocess
import shutil
import sys
import os
from typing import List

def check_java_installed() -> bool:
    """
    Check if Java is installed and available in the PATH.
    Returns True if installed, False otherwise.
    """
    if shutil.which("java"):
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return False

def get_java_install_message() -> str:
    """
    Return a message guiding the user to install Java based on their OS.
    """
    if sys.platform.startswith("linux"):
        return "Java not found. Please install it using: sudo apt install default-jre"
    elif sys.platform == "darwin":
        return "Java not found. Please install it using: brew install java"
    elif sys.platform == "win32":
        return "Java not found. Please download and install Java from https://www.java.com/download/"
    else:
        return "Java not found. Please install a Java Runtime Environment (JRE)."

def find_plantuml_files(directory: str) -> List[str]:
    """
    Find all PlantUML files in the given directory.
    Supports .pu, .puml, .plantuml extensions.
    """
    plantuml_files = []
    extensions = {'.pu', '.puml', '.plantuml'}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                plantuml_files.append(os.path.join(root, file))
                
    return plantuml_files

def convert_plantuml_to_image(files: List[str], output_format: str = 'png') -> None:
    """
    Convert PlantUML files to images using the bundled jar.
    """
    jar_path = os.path.join(os.path.dirname(__file__), 'plantuml.jar')
    
    if not files:
        print("No PlantUML files found to convert.")
        return

    # PlantUML jar can take multiple files or a directory.
    # If we pass a list of files, we can just pass them as arguments.
    # However, command line length might be an issue if there are too many files.
    # But for now, let's pass them all.
    
    cmd = ["java", "-jar", jar_path, "-t" + output_format] + files
    
    print(f"Converting {len(files)} files to {output_format}...")
    try:
        subprocess.run(cmd, check=True)
        print("Conversion complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

