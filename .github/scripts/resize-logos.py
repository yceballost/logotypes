import os
import sys
import cairosvg
from xml.etree import ElementTree as ET

def resize_svg(input_path, new_height):
    # Parse the SVG file
    tree = ET.parse(input_path)
    root = tree.getroot()
    
    # Extract width and height from the SVG
    width = float(root.get('width').replace('px', ''))
    height = float(root.get('height').replace('px', ''))
    
    # Check if the height is already correct
    if height == new_height:
        print(f'{input_path} already has the correct height.')
        return False
    
    # Calculate new dimensions while maintaining aspect ratio
    new_width = (new_height / height) * width

    # Update the width and height attributes in the SVG
    root.set('width', f'{new_width}px')
    root.set('height', f'{new_height}px')

    # Write the changes back to the file
    tree.write(input_path)
    return True

def main(folder_path, new_height):
    for filename in os.listdir(folder_path):
        if filename.endswith('.svg'):
            input_path = os.path.join(folder_path, filename)
            if resize_svg(input_path, new_height):
                print(f'Resized {filename} to height {new_height}px')
            else:
                print(f'{filename} already has the correct height.')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python resize_svgs.py <folder_path> <new_height>')
        sys.exit(1)
    folder_path = sys.argv[1]
    new_height = int(sys.argv[2])
    main(folder_path, new_height)
