import xml.etree.ElementTree as ET
import re

def mirror_path(d, center_x=2048):
    d = re.sub(r'([A-Za-z])', r' \1 ', d)
    tokens = d.split()
    mirrored = []
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd in ['M', 'L', 'm', 'l']:
            mirrored.append(cmd)
            x = float(tokens[i+1])
            y = float(tokens[i+2])
            mirrored.append(str(round(center_x * 2 - x, 3)))
            mirrored.append(str(round(y, 3)))
            i += 3
        elif cmd in ['C', 'c']:
            mirrored.append(cmd)
            x1 = float(tokens[i+1])
            y1 = float(tokens[i+2])
            x2 = float(tokens[i+3])
            y2 = float(tokens[i+4])
            x = float(tokens[i+5])
            y = float(tokens[i+6])
            mirrored.append(str(round(center_x * 2 - x1, 3)))
            mirrored.append(str(round(y1, 3)))
            mirrored.append(str(round(center_x * 2 - x2, 3)))
            mirrored.append(str(round(y2, 3)))
            mirrored.append(str(round(center_x * 2 - x, 3)))
            mirrored.append(str(round(y, 3)))
            i += 7
        elif cmd in ['Z', 'z']:
            mirrored.append('z')
            i += 1
        else:
            raise Exception("Unknown cmd: " + cmd)
    return ' '.join(mirrored)

ET.register_namespace('', 'http://www.w3.org/2000/svg')
tree = ET.parse('updatedlogo.svg')
root = tree.getroot()
paths = root.findall('{http://www.w3.org/2000/svg}path')

left_paths = paths[1:9]
hub = paths[16]

left_grad = root.find('.//{http://www.w3.org/2000/svg}linearGradient[@id="Gradient2"]')
right_grad = root.find('.//{http://www.w3.org/2000/svg}linearGradient[@id="Gradient1"]')

print("--- Analysis of Symmetry ---")
left_x1 = float(left_grad.attrib['x1'])
print(f"Left Gradient x1: {left_x1} -> If Mirrored Across x=2048, it should be: {4096 - left_x1}")
print(f"Right Gradient x1 (Actual): {float(right_grad.attrib['x1'])}")

left_d = left_paths[0].attrib['d']
right_d = paths[9].attrib['d']
print(f"Left wing start point: M {left_d.split()[1]} {left_d.split()[2]}")
print(f"Right wing start point: M {right_d.split()[1]} {right_d.split()[2]}")
print("Conclusion: The original logo was traced asymmetrically. The points, gradients, and shapes do not align perfectly when mirrored.")

perfect_svg = f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" display="block" viewBox="0 0 4096 4096" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="GradientLeft" gradientUnits="userSpaceOnUse" x1="{left_grad.attrib['x1']}" y1="{left_grad.attrib['y1']}" x2="{left_grad.attrib['x2']}" y2="{left_grad.attrib['y2']}">
      <stop offset="0" stop-opacity="1" stop-color="rgb(75,124,190)"/>
      <stop offset="1" stop-opacity="1" stop-color="rgb(157,194,242)"/>
    </linearGradient>
    <linearGradient id="GradientRight" gradientUnits="userSpaceOnUse" x1="{4096 - float(left_grad.attrib['x1'])}" y1="{left_grad.attrib['y1']}" x2="{4096 - float(left_grad.attrib['x2'])}" y2="{left_grad.attrib['y2']}">
      <stop offset="0" stop-opacity="1" stop-color="rgb(75,124,190)"/>
      <stop offset="1" stop-opacity="1" stop-color="rgb(157,194,242)"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <path fill="rgb(0,0,0)" d="M 0 0 L 4096 0 L 4096 4096 L 0 4096 L 0 0 z"/>

  <!-- Left Wing -->
'''

for p in left_paths:
    fill = p.attrib['fill']
    if fill == 'url(#Gradient2)':
        fill = 'url(#GradientLeft)'
    perfect_svg += f'  <path fill="{fill}" d="{p.attrib["d"]}"/>\n'

perfect_svg += '\n  <!-- Right Wing (Perfectly Mirrored from Left) -->\n'
for p in left_paths:
    fill = p.attrib['fill']
    if fill == 'url(#Gradient2)':
        fill = 'url(#GradientRight)'
    mirrored_d = mirror_path(p.attrib['d'])
    perfect_svg += f'  <path fill="{fill}" d="{mirrored_d}"/>\n'

hub_d = hub.attrib['d']
mirrored_hub_d = mirror_path(hub_d)

perfect_svg += f'''
  <!-- Hub (Original & Perfectly Mirrored Overlapped) -->
  <path fill="{hub.attrib['fill']}" d="{hub_d}"/>
  <path fill="{hub.attrib['fill']}" d="{mirrored_hub_d}"/>
</svg>
'''

with open('perfect.svg', 'w') as f:
    f.write(perfect_svg)

print("Generated perfect.svg successfully!")
