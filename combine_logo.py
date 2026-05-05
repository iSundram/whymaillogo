import xml.etree.ElementTree as ET
import re

def combine_logos():
    # Load Icon
    with open('logo-1.svg', 'r') as f:
        icon_content = f.read()
    
    # Load Text
    with open('logo-text.svg', 'r') as f:
        text_content = f.read()
        
    # Extract defs from icon (Gradients)
    defs_match = re.search(r'<defs>(.*?)</defs>', icon_content, re.DOTALL)
    defs_str = defs_match.group(1) if defs_match else ""
    
    # Extract paths from icon (excluding background and defs)
    # We want everything inside the <svg> except <defs> and the first white background path
    icon_paths = []
    # Find all path tags
    paths = re.findall(r'<path .*?/>', icon_content)
    for p in paths:
        if 'fill="rgb(255,255,255)"' in p:
            continue
        icon_paths.append(p)
        
    # Extract content from text svg
    # Remove empty image tags
    text_content = re.sub(r'<image.*?>', '', text_content)
    
    # Extract defs from text svg and icon svg
    text_defs_match = re.search(r'<defs.*?>(.*?)</defs>', text_content, re.DOTALL)
    text_defs_str = text_defs_match.group(1) if text_defs_match else ""
    
    # Also extract any top-level linearGradients in logo-text.svg
    text_gradients = re.findall(r'<linearGradient.*?>.*?</linearGradient>', text_content, re.DOTALL)
    text_defs_str += "\n".join(text_gradients)
    
    text_inner_match = re.search(r'<svg .*?>(.*?)</svg>', text_content, re.DOTALL)
    text_inner = text_inner_match.group(1) if text_inner_match else ""
    # Remove defs and metadata from inner content
    text_inner = re.sub(r'<defs.*?>.*?</defs>', '', text_inner, flags=re.DOTALL)
    text_inner = re.sub(r'<metadata.*?>.*?</metadata>', '', text_inner, flags=re.DOTALL)
    # Remove the gradients we already extracted
    for grad in text_gradients:
        text_inner = text_inner.replace(grad, "")
    
    # Scaling and Alignment
    text_scale = 2.66
    icon_size = 4096
    text_height = 768 * text_scale
    vertical_offset = (icon_size - text_height) / 2
    gap = 200
    total_width = icon_size + gap + (1024 * text_scale)
    
    full_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {total_width} {icon_size}" preserveAspectRatio="xMidYMid meet">
  <defs>
    {defs_str}
    {text_defs_str}
  </defs>
  <rect width="100%" height="100%" fill="white" />
  
  <!-- Icon Part -->
  <g id="icon-part">
    {" ".join(icon_paths)}
  </g>
  
  <!-- Text Part -->
  <g id="text-part" transform="translate({icon_size + gap}, {vertical_offset}) scale({text_scale})">
    {text_inner}
  </g>
</svg>
"""
    
    with open('logo-full.svg', 'w') as f:
        f.write(full_svg)
    print("logo-full.svg recreated with manual string template to avoid namespace issues.")

if __name__ == '__main__':
    combine_logos()
