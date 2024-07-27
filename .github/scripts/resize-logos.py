import os
import sys
from lxml import etree

# Conversion factors from various units to pixels
unit_conversion = {
    'px': 1,
    'mm': 3.779528,
    'cm': 37.79528,
    'in': 96,
    'pt': 1.33333,
    'pc': 16
}

def convert_to_pixels(value_with_unit):
    for unit, factor in unit_conversion.items():
        if value_with_unit.endswith(unit):
            return float(value_with_unit.replace(unit, '')) * factor
    return float(value_with_unit)  # default to pixels if no unit found

def resize_svg(input_path, new_height):
    # Parse the SVG file with lxml
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    # Extract width and height from the SVG
    width = root.get('width')
    height = root.get('height')

    if width is None or height is None:
        viewBox = root.get('viewBox')
        if viewBox:
            _, _, width, height = map(float, viewBox.split())
        else:
            raise ValueError(f"SVG file {input_path} does not have width/height attributes or viewBox.")
    else:
        width = convert_to_pixels(width)
        height = convert_to_pixels(height)

    # Check if the height is already correct
    if height == new_height:
        print(f'{input_path} already has the correct height.')
        return False

    # Calculate new dimensions while maintaining aspect ratio
    new_width = (new_height / height) * width

    # Update the width and height attributes in the SVG
    root.set('width', f'{new_width}px')
    root.set('height', f'{new_height}px')

    # Remove any existing namespace
    etree.cleanup_namespaces(root)

    # Write the changes back to the file
    tree.write(input_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
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
