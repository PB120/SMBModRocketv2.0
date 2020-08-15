import xml.etree.ElementTree as Et
fog = "F:/SMBCustomLevelStuff/SMB2_bgs/W2/forest.fog.xml"
fog_anim = "F:/SMBCustomLevelStuff/SMB2_bgs/W2/forest.foganim.xml"
f_tree = Et.parse(fog)
f_root = f_tree.getroot()
fa_tree = Et.parse(fog_anim)
fa_root = fa_tree.getroot()

fog_color = (str(0), str(0.9), str(0))
fog_type = "GX_FOG_EXP"
fog_start = str(0)
fog_end = str(300)

fog_attrs = {"red": fog_color[0], "green": fog_color[1], "blue": fog_color[2],
             "type": fog_type,
             "start": fog_start,
             "end": fog_end}

# Modify .fog.xml
# 1. fogType
for x in f_root.iter("fogType"):
    x.text = fog_type

# 2. fogStartDistance
for x in f_root.iter("fogStartDistance"):
    x.text = fog_start

# 3. fogEndDistance
for x in f_root.iter("fogEndDistance"):
    x.text = fog_end

# 4. color
for x in f_root.iter("color"):
    x[0].text = fog_attrs["red"]
    x[1].text = fog_attrs["green"]
    x[2].text = fog_attrs["blue"]

# Modify .foganim.xml

for x in fa_root.iter("startDistanceKeyframes"):
    x[0][2].text = fog_attrs["start"]
    x[1][2].text = fog_attrs["start"]

for x in fa_root.iter("endDistanceKeyframes"):
    x[0][2].text = fog_attrs["end"]
    x[1][2].text = fog_attrs["end"]

for x in fa_root.iter("redKeyframes"):
    x[0][2].text = fog_attrs["red"]
    x[1][2].text = fog_attrs["red"]

for x in fa_root.iter("greenKeyframes"):
    x[0][2].text = fog_attrs["green"]
    x[1][2].text = fog_attrs["green"]

for x in fa_root.iter("blueKeyframes"):
    x[0][2].text = fog_attrs["blue"]
    x[1][2].text = fog_attrs["blue"]

f_tree.write("F:/SMBCustomLevelStuff/SMB2_bgs/W2/practice.fog.xml", xml_declaration=True)
fa_tree.write("F:/SMBCustomLevelStuff/SMB2_bgs/W2/practice.foganim.xml", xml_declaration=True)
