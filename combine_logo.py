import re

def combine_logos():
    # Load Icon
    with open('logo-1.svg', 'r') as f:
        icon_content = f.read()
    
    # Load Text
    with open('logo-text.svg', 'r') as f:
        text_content = f.read()
        
    # 1. Extract Icon Defs
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
    
    # 4. Extract Text Inner Group
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
    
    # 5. Alignment & Margins Calculation
    icon_min_x = 384.398
    icon_min_y = 1192.36
    icon_max_x = 3711.602
    icon_max_y = 3057.73
    icon_center_y = (icon_min_y + icon_max_y) / 2
    
    text_min_x = 332.82
    text_min_y = 342.915
    text_max_x = 704.447
    text_max_y = 383.507
    text_center_y = (text_min_y + text_max_y) / 2
    
    text_scale = 25.0
    gap = 600
    
    target_text_left = icon_max_x + gap
    
    tx = target_text_left - (text_min_x * text_scale)
    
    # User felt text was a bit below center, so we shift it up slightly (e.g. -240 units)
    ty_adjustment = -240
    ty = icon_center_y - (text_center_y * text_scale) + ty_adjustment
    
    content_min_x = icon_min_x
    content_max_x = tx + (text_max_x * text_scale)
    
    content_min_y = min(icon_min_y, ty + (text_min_y * text_scale))
    content_max_y = max(icon_max_y, ty + (text_max_y * text_scale))
    
    margin = 600
    viewbox_min_x = content_min_x - margin
    viewbox_min_y = content_min_y - margin
    viewbox_width = (content_max_x - content_min_x) + (2 * margin)
    viewbox_height = (content_max_y - content_min_y) + (2 * margin)
    
    # 6. Assemble
    full_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{viewbox_min_x} {viewbox_min_y} {viewbox_width} {viewbox_height}" preserveAspectRatio="xMidYMid meet">
  <defs>
    {icon_defs}
    {text_defs_str}
  </defs>
  <rect x="{viewbox_min_x}" y="{viewbox_min_y}" width="{viewbox_width}" height="{viewbox_height}" fill="white" />
  
  <!-- Icon Part -->
  <g id="icon-part">
    {" ".join(icon_paths)}
  </g>
  
  <!-- Text Part -->
  <g id="text-part" transform="translate({tx}, {ty}) scale({text_scale})">
    {text_inner}
  </g>
</svg>
"""
    
    with open('logo-full.svg', 'w') as f:
        f.write(full_svg)
    print("logo-full.svg recreated with exact alignment and margins.")

if __name__ == '__main__':
    combine_logos()
