import pdb
import binascii
import sys
from stage_helper import paths, get_file  # temporary
import os  # temporary


def output_models(stages_dir, s_name):
    """
    Extract all model names in obj
    :param stages_dir: Path to stages folder
    :param s_name: Stage name folder
    :return: model names list ['model1', 'model2', ... so forth]
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    models = []
    line_num = 1
    obj_file = os.path.join(stage_dir, get_file(stage_dir, ".obj"))

    with open(obj_file, "r") as in_obj:
        for line in in_obj:
            if "o " in line:
                models.append((line_num - 1, line[2:-1]))
                line_num += 1

    if not models:
        print("No models found in .obj. Quitting program...")
        sys.exit(1)
    else:
        return models


def bitflag_edit(s_name, sd_name="output.lz.raw"):
    """
    Edits model bitflags in .lz.raw
    :param s_name: Stage name
    :param sd_name: file name of stage def (default="output.lz.raw")
    :return: None
    """
    stage_dir = os.path.join(paths.levels, s_name)
    sd_path = os.path.join(stage_dir, sd_name)
    bf_dict = {"0": ("Null", "00000000"),
               "1": ("Casts a shadow", "00000001"),
               "2": ("Receives a shadow", "00000002"),
               "3": ("Casts AND receives a shadow", "00000003"),
               "4": ("?", "00000004"),
               "5": ("? + Casts a shadow", "00000005"),
               "6": ("? + Receives a shadow", "00000006"),
               "7": ("? + Casts AND receives a shadow", "00000007"),
               "8": ("Transparency Type A", "00000008"),
               "9": ("Transparency Type A + Casts a shadow", "00000009"),
               "10": ("Transparency Type A + Receives a shadow", "0000000A"),
               "11": ("Transparency Type A + Casts AND receives a shadow", "0000000B"),
               "12": ("Transparency Type A + ?", "0000000C"),
               "13": ("Transparency Type A + ? + Casts a shadow", "0000000D"),
               "14": ("Transparency Type A + ? + Receives a shadow", "0000000E"),
               "15": ("Transparency Type A + ? + Casts AND receives a shadow", "0000000F"),
               "16": ("Transparency Type B", "00000010"),
               "17": ("Transparency Type B + ?", "00000011")
               }

    all_models = output_models(paths.levels, s_name)

    for model in all_models:
        print("{} ---> {}".format(model[0], model[1]))
    while True:
        model_choice = input("\nSelect number: ")
        try:
            int(model_choice)
        except ValueError:
            print("\nInvalid input.")
            continue
        else:
            pass
        if int(model_choice) < 0 or int(model_choice) > len(all_models) - 1:
            print("\nNo model associated with {}".format(int(model_choice)))
        else:
            model_choice = int(model_choice)
            model_choice = all_models[model_choice][0]
            break

    for key, value in bf_dict.items():
        print("{} ---> {}".format(key, value[0]))

    while True:
        bf_choice = input("Select bitflag effect: ")
        if bf_choice not in bf_dict.keys():
            print("Error: no match.")
        else:
            bf_choice = bf_dict[bf_choice][1]
            break

    models_offset = model_choice * 24
    lmp_a = 144 * 2  # offset value times 2 for level model pointer type A

    with open(sd_path, "rb") as sd:
        hex_bytes = sd.read()
    hex_bytes = binascii.hexlify(hex_bytes)

    bf_offset = hex_bytes[lmp_a:lmp_a + 8]  # offset value to model bit flag (hex)
    bf_offset_int = int(bf_offset, 16) * 2 + models_offset  # offset value to model bit flag * 2 (int)

    bit_flag = hex_bytes[bf_offset_int: bf_offset_int + 16]  # current model bit flag (16 chars)

    new_bit_flag = bit_flag.replace(bit_flag, "{}00000001".format(bf_choice).encode("ascii"))

    hex_bytes = hex_bytes[:bf_offset_int] + new_bit_flag + hex_bytes[bf_offset_int+16:]
    # hex with new bit flag ^

    hex_bytes = binascii.unhexlify(hex_bytes)
    with open(sd_path, "wb") as nsd:
        nsd.write(hex_bytes)


bitflag_edit("Tests")
