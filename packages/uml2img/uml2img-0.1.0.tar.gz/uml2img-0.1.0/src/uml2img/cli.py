import argparse
import sys
import os
from uml2img.core import check_java_installed, get_java_install_message, find_plantuml_files, convert_plantuml_to_image

def main():
    parser = argparse.ArgumentParser(description="Convert PlantUML files to images.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to search for PlantUML files (default: current directory)")
    parser.add_argument("-f", "--format", default="png", help="Output image format (default: png)")
    
    args = parser.parse_args()
    
    # 1. Check Java
    if not check_java_installed():
        print(get_java_install_message())
        sys.exit(1)
        
    # 2. Find files
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' not found.")
        sys.exit(1)
        
    print(f"Searching for PlantUML files in: {directory}")
    files = find_plantuml_files(directory)
    
    if not files:
        print("No PlantUML files found.")
        sys.exit(0)
        
    print(f"Found {len(files)} files.")
    
    # 3. Convert
    convert_plantuml_to_image(files, args.format)

if __name__ == "__main__":
    main()
