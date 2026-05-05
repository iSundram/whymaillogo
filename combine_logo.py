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
    # We take all paths that are NOT the white background
    icon_paths = []
    # Find all path tags, matching correctly even if they have spaces or newlines
    all_paths = re.findall(r'<path\s+[^>]*?>', icon_content, re.DOTALL)
    for p in all_paths:
        if 'fill="rgb(255,255,255)"' in p:
            continue
        # Get the full tag including closing if it exists (though here they are self-closing)
        # Re-find the full tag to be safe
        full_p_match = re.search(re.escape(p) + r'.*?/>', icon_content, re.DOTALL)
        if full_p_match:
            icon_paths.append(full_p_match.group(0))
        
    # 3. Clean up Text Content
    # Remove empty image tags correctly
    text_content = re.sub(r'<image.*?>.*?</image>', '', text_content, flags=re.DOTALL)
    text_content = re.sub(r'<image.*?/>', '', text_content)
    
    # Extract any top-level linearGradients in logo-text.svg
    text_gradients = re.findall(r'<linearGradient.*?>.*?</linearGradient>', text_content, re.DOTALL)
    text_defs_str = "\n".join(text_gradients)
    
    # 4. Extract Text Inner Group (logo-group)
    # We want exactly the <g id="logo-group"> part to be clean
    group_match = re.search(r'(<g id="logo-group">.*?</g>)\s*</svg>', text_content, re.DOTALL)
    if not group_match:
        # Fallback to general inner content if logo-group not found
        text_inner_match = re.search(r'<svg .*?>(.*?)</svg>', text_content, re.DOTALL)
        text_inner = text_inner_match.group(1) if text_inner_match else ""
    else:
        text_inner = group_match.group(1)
        
    # Clean inner text from metadata/defs/images again to be double sure
    text_inner = re.sub(r'<metadata.*?>.*?</metadata>', '', text_inner, flags=re.DOTALL)
    text_inner = re.sub(r'<defs.*?>.*?</defs>', '', text_inner, flags=re.DOTALL)
    for grad in text_gradients:
        text_inner = text_inner.replace(grad, "")
    
    # 5. Scaling and Alignment
    icon_size = 4096
    text_scale = 3.5 # Slightly larger for better readability
    text_height = 768 * text_scale
    vertical_offset = (icon_size - text_height) / 2
    gap = 400 # More generous gap
    total_width = icon_size + gap + (1024 * text_scale)
    
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
  <g id="text-part" transform="translate({icon_size + gap}, {vertical_offset}) scale({text_scale})">
    {text_inner}
  </g>
</svg>
"""
    
    with open('logo-full.svg', 'w') as f:
        f.write(full_svg)
    print("logo-full.svg recreated with cleaner extraction.")

if __name__ == '__main__':
    combine_logos()
