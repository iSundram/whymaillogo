import xml.etree.ElementTree as ET
import re

def bezier_split(p0, p1, p2, p3, t):
    """Splits a cubic bezier curve into two at parameter t.
    Returns (left_curve, right_curve) where each curve is a tuple of 4 points.
    """
    def lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    p01 = lerp(p0, p1, t)
    p12 = lerp(p1, p2, t)
    p23 = lerp(p2, p3, t)

    p012 = lerp(p01, p12, t)
    p123 = lerp(p12, p23, t)

    p0123 = lerp(p012, p123, t)

    return (p0, p01, p012, p0123), (p0123, p123, p23, p3)

def round_svg_corner():
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    tree = ET.parse('perfect.svg')
    root = tree.getroot()

    def replace_left(match):
        # We match: C 1647.95 2866.35 1602.97 2970.24 1564.07 3054.47 L 1147.89 3054.55
        p0 = (1689.5, 2785.04) # this is the point before the 'C', we know from looking at perfect.svg
        p1 = (1647.95, 2866.35)
        p2 = (1602.97, 2970.24)
        p3 = (1564.07, 3054.47)
        
        # Split bezier at t=0.9
        left, right = bezier_split(p0, p1, p2, p3, 0.85)
        
        # New end of bezier is left[3]
        new_p3 = left[3]
        
        # We need a corner curve from new_p3 to a point on the line
        # The line goes from p3 to (1147.89, 3054.55).
        # We want the corner curve to be tangent to the bezier at new_p3, and tangent to the line.
        # Let's just use a Q curve from new_p3 with control point right[3] (which is p3) 
        # and end point slightly along the line.
        line_end = (1147.89, 3054.55)
        
        # To make it smooth, let's find the intersection of the tangent at new_p3 and the line.
        # Actually, right[3] is exactly the intersection!
        # Because right[3] = p3, which is the end of the original bezier and the start of the line.
        # But wait, Q curve needs to be tangent to the line at the end point.
        # The line is y = 3054.47 to 3054.55, essentially horizontal.
        # If we use p3 as the control point for a Q curve, its tangents will go exactly through new_p3 and the end point!
        # What should the end point on the line be?
        # A good symmetric-looking corner puts the end point at distance `d` along the line, 
        # where `d` is the distance from p3 to new_p3.
        import math
        dist = math.hypot(p3[0] - new_p3[0], p3[1] - new_p3[1])
        
        # Vector along the line
        dx = line_end[0] - p3[0]
        dy = line_end[1] - p3[1]
        line_len = math.hypot(dx, dy)
        end_x = p3[0] + (dx / line_len) * dist
        end_y = p3[1] + (dy / line_len) * dist
        
        # Format the new string
        # C new_p1_x new_p1_y new_p2_x new_p2_y new_p3_x new_p3_y Q p3_x p3_y end_x end_y L line_end_x line_end_y
        res = f"C {left[1][0]:.3f} {left[1][1]:.3f} {left[2][0]:.3f} {left[2][1]:.3f} {left[3][0]:.3f} {left[3][1]:.3f} "
        res += f"Q {p3[0]:.3f} {p3[1]:.3f} {end_x:.3f} {end_y:.3f} L {line_end[0]:.3f} {line_end[1]:.3f}"
        return res

    def replace_right(match):
        # Mirrored coordinates for the right side
        p0 = (4096 - 1689.5, 2785.04) 
        p1 = (4096 - 1647.95, 2866.35)
        p2 = (4096 - 1602.97, 2970.24)
        p3 = (4096 - 1564.07, 3054.47)
        line_end = (4096 - 1147.89, 3054.55)

        left, right = bezier_split(p0, p1, p2, p3, 0.85)
        new_p3 = left[3]

        import math
        dist = math.hypot(p3[0] - new_p3[0], p3[1] - new_p3[1])
        
        dx = line_end[0] - p3[0]
        dy = line_end[1] - p3[1]
        line_len = math.hypot(dx, dy)
        end_x = p3[0] + (dx / line_len) * dist
        end_y = p3[1] + (dy / line_len) * dist

        res = f"C {left[1][0]:.3f} {left[1][1]:.3f} {left[2][0]:.3f} {left[2][1]:.3f} {left[3][0]:.3f} {left[3][1]:.3f} "
        res += f"Q {p3[0]:.3f} {p3[1]:.3f} {end_x:.3f} {end_y:.3f} L {line_end[0]:.3f} {line_end[1]:.3f}"
        return res

    with open('perfect.svg', 'r') as f:
        content = f.read()

    # Left
    left_pattern = r'C\s+1647\.95\s+2866\.35\s+1602\.97\s+2970\.24\s+1564\.07\s+3054\.47\s+L\s+1147\.89\s+3054\.55'
    content = re.sub(left_pattern, replace_left, content)

    # Right
    right_pattern = r'C\s+2448\.05\s+2866\.35\s+2493\.03\s+2970\.24\s+2531\.93\s+3054\.47\s+L\s+2948\.11\s+3054\.55'
    content = re.sub(right_pattern, replace_right, content)

    with open('logo-1.svg', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    round_svg_corner()
    print("logo-1.svg generated successfully.")
