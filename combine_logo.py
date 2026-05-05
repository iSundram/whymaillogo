import re

def combine_logos():
    # Load Icon
    with open('logo-1.svg', 'r') as f:
        icon_content = f.read()
    
    # Load Text
    with open('logo-text.svg', 'r') as f:
        text_content = f.read()
        
    # 1. Extract Icon Defs (Gradients)
    defs_match = re.search(r'<defs>(.*?)</defs>', icon_content, re.DOTALL)
    icon_defs = defs_match.group(1) if defs_match else ""
    
    # 2. Extract Icon Paths
    icon_paths = []
    all_paths = re.findall(r'<path\s+[^>]*?>', icon_content, re.DOTALL)
    for p in all_paths:
        if 'fill="rgb(255,255,255)"' in p:
            continue
        full_p_match = re.search(re.escape(p) + r'.*?/>', icon_content, re.DOTALL)
        if full_p_match:
            icon_paths.append(full_p_match.group(0))
        
    # 3. Clean up Text Content
    text_content = re.sub(r'<image.*?>.*?</image>', '', text_content, flags=re.DOTALL)
    text_content = re.sub(r'<image.*?/>', '', text_content)
    
    text_gradients = re.findall(r'<linearGradient.*?>.*?</linearGradient>', text_content, re.DOTALL)
    text_defs_str = "\n".join(text_gradients)
    
    # 4. Extract Text Inner Group (logo-group)
    group_match = re.search(r'(<g id="logo-group">.*?</g>)\s*</svg>', text_content, re.DOTALL)
    if not group_match:
        text_inner_match = re.search(r'<svg .*?>(.*?)</svg>', text_content, re.DOTALL)
        text_inner = text_inner_match.group(1) if text_inner_match else ""
    else:
        text_inner = group_match.group(1)
        
    text_inner = re.sub(r'<metadata.*?>.*?</metadata>', '', text_inner, flags=re.DOTALL)
    text_inner = re.sub(r'<defs.*?>.*?</defs>', '', text_inner, flags=re.DOTALL)
    for grad in text_gradients:
        text_inner = text_inner.replace(grad, "")
    
    # 5. Scaling and Alignment
    # The actual bounding box of the text inside logo-text.svg:
    min_x = 332.8
    min_y = 342.9
    actual_text_width = 371.6
    actual_text_height = 40.6
    
    icon_size = 4096
    text_scale = 32.5  # Reduced by half as requested
    
    scaled_text_width = actual_text_width * text_scale
    scaled_text_height = actual_text_height * text_scale
    
    vertical_offset = (icon_size - scaled_text_height) / 2
    gap = 800
    total_width = icon_size + gap + scaled_text_width
    
    # 6. Assemble
    full_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {total_width} {icon_size}" preserveAspectRatio="xMidYMid meet">
  <defs>
    {icon_defs}
    {text_defs_str}
  </defs>
  <rect width="100%" height="100%" fill="white" />
  
  <!-- Icon Part -->
  <g id="icon-part">
    {" ".join(icon_paths)}
  </g>
  
  <!-- Text Part -->
  <g id="text-part" transform="translate({icon_size + gap}, {vertical_offset}) scale({text_scale}) translate({-min_x}, {-min_y})">
    {text_inner}
  </g>
</svg>
"""
    
    with open('logo-full.svg', 'w') as f:
        f.write(full_svg)
    print("logo-full.svg recreated with proper offset zeroing.")

if __name__ == '__main__':
    combine_logos()
