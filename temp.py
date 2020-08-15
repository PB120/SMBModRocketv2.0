import xml.etree.ElementTree as Et
fog = "F:/SMBCustomLevelStuff/SMB2_bgs/W2/forest.fog.xml"
fog_anim = "F:/SMBCustomLevelStuff/SMB2_bgs/W2/forest.foganim.xml"
fog_tree = Et.parse(fog)
fog_root = fog_tree.getroot()

fog_color = (str(0.45), str(0.75), str(0.95))
fog_type = "GX_FOG_EXP"
fog_start = str(-10)
fog_end = str(60000)

fog_attrs = {"red": fog_color[0], "green": fog_color[1], "blue": fog_color[2],
             "type": fog_type,
             "start": fog_start,
             "end": fog_end}

for x in fog_root[3]:
    print(x.tag)

# Modify xml
# 1. fogType
for x in fog_root.iter("fogType"):
    x.text = fog_type

# 2. fogStartDistance
for x in fog_root.iter("fogStartDistance"):
    x.text = fog_start

# 3. fogEndDistance
for x in fog_root.iter("fogEndDistance"):
    x.text = fog_end

# 4. color
for x in fog_root.iter("color"):
    x[0].text = fog_attrs["red"]
    x[1].text = fog_attrs["green"]
    x[2].text = fog_attrs["blue"]

fog_tree.write("F:/SMBCustomLevelStuff/SMB2_bgs/W2/practice.fog.xml", xml_declaration=True)
