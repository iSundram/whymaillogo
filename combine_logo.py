import xml.etree.ElementTree as ET
import re

def combine_logos():
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    
    # Load Icon
    tree_icon = ET.parse('logo-1.svg')
    root_icon = tree_icon.getroot()
    
    # Load Text
    tree_text = ET.parse('logo-text.svg')
    root_text = tree_text.getroot()
    
    # Get defs from icon
    defs_icon = root_icon.find('.//{http://www.w3.org/2000/svg}defs')
    
    # Create Full Logo SVG
    # We'll use height 4096.
    # Icon width = 4096.
    # Text height 4096 (scaled from 768). Scale = 4096/768 = 5.333333333333333
    text_scale = 4096 / 768
    text_width = 1024 * text_scale
    gap = 200
    total_width = 4096 + gap + text_width
    total_height = 4096
    
    full_svg = ET.Element('svg', {
        'version': '1.1',
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'viewBox': f'0 0 {total_width} {total_height}',
        'display': 'block',
        'preserveAspectRatio': 'xMidYMid meet'
    })
    
    # Add merged defs
    full_defs = ET.SubElement(full_svg, 'defs')
    if defs_icon is not None:
        for child in defs_icon:
            full_defs.append(child)
            
    # Add background
    ET.SubElement(full_svg, 'rect', {
        'width': '100%',
        'height': '100%',
        'fill': 'rgb(255,255,255)'
    })
    
    # Add Icon Group
    icon_g = ET.SubElement(full_svg, 'g', {'id': 'icon-part'})
    for child in root_icon:
        if child.tag.endswith('defs') or 'rect' in child.tag or ('path' in child.tag and child.attrib.get('fill') == 'rgb(255,255,255)'):
            continue
        icon_g.append(child)
        
    # Add Text Group
    text_g = ET.SubElement(full_svg, 'g', {
        'id': 'text-part',
        'transform': f'translate({4096 + gap}, 0) scale({text_scale})'
    })
    for child in root_text:
        if child.tag.endswith('defs') or child.tag.endswith('metadata'):
            continue
        text_g.append(child)
        
    # Save
    tree_full = ET.ElementTree(full_svg)
    tree_full.write('logo-full.svg', xml_declaration=True, encoding='utf-8')
    print("logo-full.svg created successfully!")

if __name__ == '__main__':
    combine_logos()
