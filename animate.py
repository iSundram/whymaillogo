import xml.etree.ElementTree as ET
import re
import math

def calculate_path_length(d):
    """Estimate path length by summing distances between absolute coordinates.
    Since doing exact Bezier arc length in python is complex, we just sum
    the straight line distance between the control points/endpoints to get a conservative 
    overestimate of the length to use for stroke-dasharray.
    """
    length = 0
    current_pos = (0, 0)
    
    # Simple regex to get all coordinates
    coords = re.findall(r'[-+]?\d*\.\d+|\d+', d)
    coords = [float(c) for c in coords]
    
    # We will just take pairs of coordinates and calculate the distance
    # to the next pair. It's an approximation but good enough for stroke-dasharray
    # if we add a 20% buffer.
    points = [(coords[i], coords[i+1]) for i in range(0, len(coords)-1, 2)]
    
    if not points:
        return 20000 # fallback
        
    current_pos = points[0]
    for p in points[1:]:
        length += math.hypot(p[0] - current_pos[0], p[1] - current_pos[1])
        current_pos = p
        
    return int(length * 1.3) # Add 30% to ensure it fully covers the curve

def create_animated_svg():
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse('logo-1.svg')
    root = tree.getroot()
    
    # We need to add a <style> block to the defs
    defs = root.find('.//{http://www.w3.org/2000/svg}defs')
    if defs is None:
        defs = ET.Element('{http://www.w3.org/2000/svg}defs')
        root.insert(0, defs)
        
    style = ET.Element('{http://www.w3.org/2000/svg}style')
    
    css = """
    @keyframes drawStroke {
        to { stroke-dashoffset: 0; }
    }
    @keyframes fadeInFill {
        to { fill-opacity: 1; }
    }
    @keyframes fadeOutStroke {
        to { stroke-opacity: 0; filter: blur(4px); }
    }
    
    path {
        fill-opacity: 0;
        stroke-opacity: 1;
        stroke-width: 15;
        stroke-linecap: round;
        stroke-linejoin: round;
    }
    
    /* Background shouldn't animate */
    path:nth-of-type(1) {
        fill-opacity: 1;
        stroke: none;
        animation: none;
    }
    """
    
    paths = root.findall('.//{http://www.w3.org/2000/svg}path')
    
    # Skip background (index 0)
    for i, path in enumerate(paths[1:], start=1):
        d = path.get('d', '')
        fill = path.get('fill', 'rgb(255,255,255)')
        
        # Determine stroke color (same as fill, unless it's a gradient, then pick a fallback solid color)
        stroke_color = fill
        if 'url' in fill:
            stroke_color = 'rgb(100, 150, 220)' # approximation of the blue gradient
            
        length = calculate_path_length(d)
        
        # Base class name for the animation delay
        class_name = f"path-{i}"
        path.set('class', class_name)
        
        delay_draw = (i - 1) * 0.15
        delay_fill = 1.2 + (i - 1) * 0.05
        delay_fade = 1.5 + (i - 1) * 0.05
        
        if i in [1, 9]:
            # Main wing backgrounds: animate the stroke
            css += f"""
            .{class_name} {{
                stroke: {stroke_color};
                stroke-dasharray: {length};
                stroke-dashoffset: {length};
                animation: 
                    drawStroke 2.0s cubic-bezier(0.25, 1, 0.5, 1) {delay_draw}s forwards,
                    fadeInFill 1.0s ease {delay_fill}s forwards,
                    fadeOutStroke 0.8s ease {delay_fade}s forwards;
            }}
            """
        else:
            # Inner details & hub: no stroke, just fade in the fill
            css += f"""
            .{class_name} {{
                stroke: none;
                animation: fadeInFill 1.0s ease {delay_fill}s forwards;
            }}
            """
        
    style.text = css
    defs.append(style)
    
    tree.write('animate.svg', xml_declaration=True, encoding='utf-8')

if __name__ == '__main__':
    create_animated_svg()
    print("animate.svg created!")
