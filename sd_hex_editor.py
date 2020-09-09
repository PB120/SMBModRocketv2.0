# import pdb
import binascii

"""
00000000: Null
00000001: Casts a shadow
00000002: Receives a shadow
00000003: Casts AND receives a shadow
00000004: ?
00000005: ? + Casts a shadow
00000006: ? + Receives a shadow
00000007: ? + Casts AND receives a shadow
00000008: Transparency Type A
00000009: Transparency Type A + Casts a shadow
0000000A: Transparency Type A + Receives a shadow
0000000B: Transparency Type A + Casts AND receives a shadow
0000000C: Transparency Type A + ?
0000000D: Transparency Type A + ? + Casts a shadow
0000000E: Transparency Type A + ? + Receives a shadow
0000000F: Transparency Type A + ? + Casts AND receives a shadow
00000010: Transparency Type B
00000011: Transparency Type B +

"""

models_offset = int(input("Input model offset: ")) * 24

lmp_typeA = 144 * 2  # offset value times 2 for level model pointer type A

with open("F:/SMBCustomLevelStuff/Levels/Tests/output.lz.raw", "rb") as sd:
    hex_bytes = sd.read()
hex_bytes = binascii.hexlify(hex_bytes)
hex_bytes_str = str(hex_bytes)[2:-1].upper()

bf_offset = hex_bytes_str[lmp_typeA:lmp_typeA + 8]  # offset value to model bit flag (hex)
bf_offset_int = int(bf_offset, 16) * 2 + models_offset  # offset value to model bit flag * 2 (int)
print(bf_offset_int)

bit_flag = hex_bytes_str[bf_offset_int: bf_offset_int + 16]  # current model bit flag (16 chars)

new_bit_flag = bit_flag.replace(bit_flag, "0000000100000001")
print(bit_flag)

hex_bytes_str = hex_bytes_str[:bf_offset_int] + new_bit_flag + hex_bytes_str[bf_offset_int+16:]
# hex str with new bit flag ^

bit_flag = hex_bytes_str[bf_offset_int: bf_offset_int + 16]
hex_bytes = hex_bytes_str.encode('ascii')
hex_bytes = binascii.unhexlify(hex_bytes)
print(bit_flag)
with open("F:/SMBCustomLevelStuff/Levels/Tests/output.lz.raw", "wb") as nsd:
    nsd.write(hex_bytes)
