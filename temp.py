"""Automates creation, renaming and moving of SMB stage files"""
import argparse
import ast
import sys
import subprocess
import os
import shutil
import xml.etree.ElementTree as Et
import config_writer
import re
import time
import config_writer as cw
import configparser
from pdb import set_trace
from tkinter import colorchooser as cc
from tkinter import Tk

config = configparser.ConfigParser()
parser = configparser.ConfigParser()

cw.exec_main_block()
parser.read("config.ini")

paths = cw.Paths(parser.get("Paths/directories", "levels"),
                 parser.get("Paths/directories", "ws2"),
                 parser.get("Paths/directories", "ws2ify"),
                 parser.get("Paths/directories", "bgtool"),
                 parser.get("Paths/directories", "SMBFogTool"),
                 parser.get("Paths/directories", "SMB_LZ_Tool"),
                 parser.get("Paths/directories", "gmatool"),
                 parser.get("Paths/directories", "gxmodelviewer"),
                 parser.get("Paths/directories", "gxmodelviewernogui"),
                 parser.get("Paths/directories", "iso"),
                 parser.get("Paths/directories", "root"),
                 parser.get("Paths/directories", "gcr"),
                 parser.get("Paths/directories", "playtest"),
                 parser.get("Paths/directories", "Dolphin")
                 )


def cl():
    """
    Command line interface for SMBModRocket functions
    :return: dictionary - {command line flag: value}
    """
    cl_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                        description="SMBModRocket is a tool to automate production "
                                                    "of SMB stage files and usage of "
                                                    "other modding software built by the SMB community.\n\n"
                                                    "** Commands that require a stage directory and/or stage index "
                                                    "are marked with an \'S\' **"
                                                    "\n "
                                        )

    cl_parser.add_argument('-stage_dir', type=str, help='Stage XML and OBJ directory')
    cl_parser.add_argument('-index', type=int, help='Stage index (any number between 1-350)')
    cl_parser.add_argument('-0S', action='store_true', help='Build stage def')
    cl_parser.add_argument('-1S', action='store_true', help='Compress existing stage def into LZ')
    cl_parser.add_argument('-2S', action='store_true', help='Build stage def and compress into LZ')
    cl_parser.add_argument('-3S', action='store_true', help='Apply bg data to existing stage def')
    cl_parser.add_argument('-4aS', action='store_true', help='Edit data in existing .fog.xml and .foganim.xml')
    cl_parser.add_argument('-4bS', action='store_true', help='Copy fog data from existing xmls to stage def')
    cl_parser.add_argument('-4cS', action='store_true', help='Copy data from source stage def to destination stage def')
    cl_parser.add_argument('-4dS', action='store_true', help='Extract fog xmls from stage def')
    cl_parser.add_argument('-5S', action='store_true', help='Build stage GMA/TPL')
    cl_parser.add_argument('-6S', action='store_true', help='Merge GMA/TPLs')
    cl_parser.add_argument('-7S', action='store_true', help='Edit stage slot in usa.str file')
    cl_parser.add_argument('-8S', action='store_true', help='Move stage files to ISO stage folder')
    cl_parser.add_argument('-9', action='store_true', help='Playtest game')
    cl_parser.add_argument('-10', action='store_true', help='Rebuild ISO')

    args = cl_parser.parse_args()
    args_str = str(args)
    args_str = str(args)[args_str.find('(') + 1: args_str.find(')', -1)]
    x = args_str.split(", **")[0].split(" ")
    x = "".join(x).split(",")
    s_args = {}  # -stage_dir and -index flags and values
    for arg in x:
        s_args[arg[:arg.find("=")]] = ast.literal_eval(arg[arg.find("=") + 1:])

    other_args = args_str.split(", **")[1]
    other_args = ast.literal_eval(other_args)  # all other flags and values
    s_args.update(other_args)
    args_dict = s_args

    if len(sys.argv) < 2:
        cl_parser.print_help()
        sys.exit(1)

    return args_dict


cl_dict = cl()


def get_file(path, extension, override=False):
    """
    Grab filename of a file inside a specific directory that has a specific file extension

    :param path: file path
    :param extension: file extension
    :param override: bool
    :return: File name if the number of files with specified extension >= 1.
    Else, returns None.
    """

    num_lst = []
    ext_lst = []
    ext_count = -1
    for f_name in os.listdir(path):
        if f_name.endswith(extension):
            ext_count += 1
            ext_lst.append(f_name)
            num_lst.append(ext_count)

    if len(ext_lst) == 0:
        return ext_lst

    elif len(ext_lst) == 1:
        return ext_lst[0]

    else:

        if override:
            return True

        else:
            while True:
                files = [file for file in ext_lst]
                files_zip = list(zip(num_lst, files))
                print("\nMultiple {} files available\n".format(extension))
                for ele in files_zip:
                    print("{} ---> {}".format(ele[0], ele[1]))
                try:
                    file_num = int(input("\nChoose number corresponding to .xml file: ".format(extension)))
                except ValueError:
                    print("Invalid input.")
                else:
                    file_num = int(file_num)
                    if file_num in num_lst:
                        return files_zip[file_num][1]
                    else:
                        print("Number not available.")


def get_obj(xml_path):
    """
    Grabs obj filename found in xml file

    :param xml_path: xml path and file name
    :return: obj filename
    """
    file = xml_path
    tree = Et.parse(file)
    root = tree.getroot()
    obj = ""

    for child in root:
        if child.tag == "modelImport":
            obj = child.text.split("/")[-1]

    return obj


def stage_num():
    """
    Prompts user for stage number and converts it to a 3-digit string

    :return: Stage number for LZ/GMA/TPL (str)
    """
    first = 1
    last = 350

    while True:
        s_num = input("Enter stage number (1-350). No input will yield default 001. ")
        if s_num == "":
            s_num = "001"
            return s_num
        else:
            try:
                s_num = int(s_num)
            except ValueError:
                print("\nInvalid stage number! Try again.")
            else:
                if s_num < first or s_num > last:
                    print("Invalid stage number! Try again.")
                else:
                    s_num = "{:03d}".format(s_num)
                    return s_num


def stage_name(stages_dir):
    """
    Show user the stages that are available. Return user-selected stage name.

    :param stages_dir: Directory of stage folders
    :return: Name of specified stage
    """

    print("\nAVAILABLE STAGES:"
          "\n")

    stages_dir = os.path.expanduser(stages_dir)
    os.chdir(stages_dir)
    stage_lst = next(os.walk('.'))[1]
    stage_lst_up = [name.upper() for name in stage_lst]
    num_lst = [str(num) for num in range(len(stage_lst_up))]
    zipped_list = list(zip(num_lst, stage_lst_up))

    os.chdir(config_writer.tool_path)

    for stage in zipped_list:
        print("{} ---> {}".format(stage[0], stage[1]))
    while True:
        stg_input = input("\nEnter stage name or number associated with stage name: ")
        if stg_input.upper() not in stage_lst_up and stg_input not in num_lst:
            print("\nStage name not found.")
        elif stg_input in num_lst:
            return stage_lst_up[int(stg_input)]
        else:
            return stg_input


def txt_to_xml(ws2ify_path, stage_dir):
    """
    Runs ws2ify to convert txt to xml config

    :param ws2ify_path: ws2ify run.py file path
    :param stage_dir: Path to stage folder

    :return: If ws2ify is used, returns xml file name. Else, returns None.
    """

    txt_file = get_file(stage_dir, ".txt", override=True)
    obj_file = get_file(stage_dir, ".obj", override=True)
    keyframe_easing_dict = {"1": "LINEAR", "2": "EASED"}

    # If both an obj and txt file exist, user can use ws2ify
    if txt_file and obj_file:

        while True:
            use_ws2ify = input("\nTXT exists. Use ws2ify? (Y/N) ")
            if use_ws2ify:
                use_ws2ify = use_ws2ify.upper()[0]

            if use_ws2ify != "Y" and use_ws2ify != "N":
                print("\nInvalid input.")
            elif use_ws2ify == "N":
                return None
            else:
                break

        txt_file = get_file(stage_dir, ".txt", override=False)
        obj_file = get_file(stage_dir, ".obj", override=False)
        txt_path = os.path.join(stage_dir, txt_file)
        obj_path = os.path.join(stage_dir, obj_file)

        while True:
            keyframe_easing = input("\nKeyframe easing = linear(1) or eased(2)?: ")
            if keyframe_easing != "1" and keyframe_easing != "2":
                print("\nInvalid input.")
            else:
                keyframe_easing = keyframe_easing_dict[keyframe_easing]
                break

        xml = "{}.xml".format(input("\nOutput xml filename: "))
        xml_path = os.path.join(stage_dir, xml)

        ws2ify_path = os.path.expanduser(ws2ify_path)
        os.chdir(ws2ify_path)
        subprocess.call(["python", "run.py", txt_path, obj_path, xml_path, keyframe_easing])
        os.chdir(config_writer.tool_path)

        return xml


def apply_bg_data(stage_dir, bgfiles_path):
    """

    :param stage_dir: directory of stage folder
    :param bgfiles_path: bgfiles folder path
    :return: None
    """
    os.chdir(bgfiles_path)
    all_bg_themes = set([re.split('[^a-zA-Z0-9]', file)[0]
                         for file in os.listdir(bgfiles_path) if file != "bgtool.exe"])

    [print(theme) for theme in all_bg_themes]
    while True:
        bg_choice = input("\nSelect bg: ")
        if bg_choice not in all_bg_themes:
            print("Bg not found.")
        else:
            break

    subprocess.call(["bgtool.exe", "{}\\output.lz.raw".format(stage_dir), "-r", bg_choice])

    src = os.path.join(stage_dir, "output.lz.raw_newbg")
    dst = os.path.join(stage_dir, "output.lz.raw")
    if os.path.isfile(dst):
        os.remove(dst)
    os.rename(src, dst)

    os.chdir(config_writer.tool_path)


def stage_def_to_lz(s_name, s_number, stages_dir, ws2ify_path, ws2_fe_dir, lz_tool_dir, return_xml=False):
    """
    Run lz_both.bat file with the following command line arguments (in order):
        (1) ws2lzfrontend.exe directory, (2) stages directory,
        (3) stage name, (4) stage xml filename, (5) SMB_LZ_Tool directory

    :param s_name: Stage name
    :param s_number: Stage number
    :param ws2ify_path: Path to ws2ify run.py file
    :param ws2_fe_dir: Directory containing ws2lzfrontend.exe file
    :param lz_tool_dir: Directory containing SMB_LZ_Tool.exe file
    :param return_xml: Bool
    :param stages_dir: Directory of stage folders
    :return: True -> return xml file name; False -> return None
    """

    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    xml_file = txt_to_xml(ws2ify_path, stage_dir)

    if not xml_file:
        xml_file = get_file(stage_dir, ".xml", override=False)

    if not xml_file:
        print("\nNo XML exists. Quitting program...")
        sys.exit(1)

    obj_file = get_obj(os.path.join(stage_dir, xml_file))

    # Check if obj filename pulled from xml file exists in stage folder
    if not os.path.isfile(os.path.join(stage_dir, obj_file)):
        print("{} does not exist in {}. Quitting program...".format(obj_file, stage_dir))
        sys.exit(1)

    subprocess.call(["lz_both.bat", ws2_fe_dir, stages_dir, s_name, xml_file, lz_tool_dir])
    os.remove(os.path.join(stage_dir, "output.lz.raw"))

    src = os.path.join(stage_dir, "output.lz.raw.lz")
    dst = os.path.join(stage_dir, "STAGE{}.lz".format(s_number))
    if os.path.isfile(dst):
        os.remove(dst)
    os.rename(src, dst)

    if return_xml:
        return xml_file


def stage_def(s_name, stages_dir, ws2ify_path, ws2_fe_dir, bgfiles_path):
    """
    Run lz_raw.bat file with the following command line arguments (in order):
        (1) ws2lzfrontend.exe directory, (2) stages directory,
        (3) stage name, (4) stage xml filename

    :param s_name: Stage name
    :param ws2ify_path: Path to ws2ify run.py file
    :param ws2_fe_dir: Directory containing ws2lzfrontend.exe file
    :param bgfiles_path: bgtool path
    :param stages_dir: Directory of stage folders
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    xml_file = txt_to_xml(ws2ify_path, stage_dir)

    if not xml_file:
        xml_file = get_file(stage_dir, ".xml", override=False)

    obj_file = get_obj(os.path.join(stage_dir, xml_file))
    raw_lz_file = "output.lz.raw"

    # Check if obj filename pulled from xml file exists in stage_dir
    if not os.path.isfile(os.path.join(stage_dir, obj_file)):
        print("{} does not exist in {}. Quitting program...".format(obj_file, stage_dir))
        sys.exit(1)

    if os.path.isfile(os.path.join(stage_dir, raw_lz_file)):
        while True:
            overwrite_input = input("{} already exists in {}. Overwrite? (Y/N) ".format(raw_lz_file, stage_dir))
            if overwrite_input.lower() == "":
                print("Input not recognized! Try again.")
            elif overwrite_input.lower()[0] != 'y' and overwrite_input.lower()[0] != 'n':
                print("Input not recognized! Try again.")
            elif overwrite_input.lower()[0] == 'n':
                break
            else:
                subprocess.call(["lz_raw.bat", ws2_fe_dir, stages_dir, s_name, xml_file])
                break

    else:
        subprocess.call(["lz_raw.bat", ws2_fe_dir, stages_dir, s_name, xml_file])

    while True:
        user_choice = input("\nApply vanilla BG? (Y/N) ")
        if len(user_choice) == 0 or (user_choice.upper()[0] != "Y" and user_choice.upper()[0] != "N"):
            print("\nInvalid input.\n")
        elif user_choice.upper()[0] == "N":
            break
        else:
            apply_bg_data(stage_dir, bgfiles_path)
            break


def fog_ops(s_name, stages_dir, fog_tool_dir):
    """
    Allows user to use all functions in SMBFogTool and edit color choice and fog boundaries in fog xmls
    :return:
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    file_raw = get_file(stage_dir, ".raw", override=True)
    file_lz = get_file(stage_dir, ".lz", override=True)
    if not file_raw and not file_lz:
        print("No .lz or .lz.raw available. Quitting program...")
        sys.exit(1)
    elif not file_raw:
        if type(file_lz) == bool:
            file_lz = get_file(stage_dir, ".lz", override=False)
        subprocess.call([paths.smb_lz_tool, file_lz])

    raw_lz_file = "output.lz.raw"
    fog_tool_executable = os.path.join(fog_tool_dir, "SMBFogTool.exe")
    lzraw = os.path.join(stage_dir, raw_lz_file)

    def edit_fog_xml():
        """
        Edit fog color choice, fog type, and fog boundaries in fog XMLs
        :return: None
        """
        fog_types = {"NONE": "GX_FOG_NONE", "LIN": "GX_FOG_LIN",
                     "EXP": "GX_FOG_EXP", "EXP2": "GX_FOG_EXP2",
                     "REXP": "GX_FOG_REVEXP", "REXP2": "GX_FOG_REVEXP2"}

        while True:
            source_xml = input("Enter source xml directory and shared file name (ex: \"water\" for water.fog.xml "
                               "and water.foganim.xml): ")
            fog = "{}.fog.xml".format(source_xml)
            fog_anim = "{}.foganim.xml".format(source_xml)
            if not os.path.isfile(fog) and not os.path.isfile(fog_anim):
                print("\n{} not found.".format(fog))
                print("{} not found.".format(fog_anim))
            elif not os.path.isfile(fog):
                print("\n{} not found.".format(fog))
            elif not os.path.isfile(fog_anim):
                print("\n{} not found.".format(fog_anim))
            else:
                break

        def color():
            """

            :return: Tuple with user-selected RGB fractions
            """
            root = Tk()
            output_color = []
            print("\nSelect fog color from GUI")
            while True:
                my_color = cc.askcolor()[0]
                if not my_color:
                    print("Error: no color selected.")
                else:
                    break
            for rgb_value in my_color:
                if rgb_value > 255:
                    rgb_value = 255
                output_color.append(str(rgb_value / 255))
            output_color = tuple(output_color)
            root.destroy()
            return output_color

        # Select fog RGB
        fog_color = color()

        # Select fog type
        while True:
            print("\nFog types: {}".format(", ".join(list(fog_types.keys()))))
            fog_select = input("\nSelect fog type: ").upper()
            if fog_select not in fog_types.keys():
                print("Fog type not found.")
            else:
                fog_type = fog_types[fog_select]
                break
        # Select fog start distance
        while True:
            fog_start = input("Fog start distance: ")
            try:
                float(fog_start)
            except ValueError:
                print("Invalid input.")
            else:
                break
        # Select fog end distance
        while True:
            fog_end = input("Fog end distance: ")
            try:
                float(fog_end)
            except ValueError:
                print("Invalid input.")
            else:
                break

        fog_attrs = {"red": fog_color[0], "green": fog_color[1], "blue": fog_color[2],
                     "type": fog_type,
                     "start": fog_start,
                     "end": fog_end}

        f_tree = Et.parse(fog)
        f_root = f_tree.getroot()
        fa_tree = Et.parse(fog_anim)
        fa_root = fa_tree.getroot()

        # Modify .fog.xml
        # 1. fogType
        for ele in f_root.iter("fogType"):
            ele.text = fog_type

        # 2. fogStartDistance
        for ele in f_root.iter("fogStartDistance"):
            ele.text = fog_start

        # 3. fogEndDistance
        for ele in f_root.iter("fogEndDistance"):
            ele.text = fog_end

        # 4. color
        for ele in f_root.iter("color"):
            ele[0].text = fog_attrs["red"]
            ele[1].text = fog_attrs["green"]
            ele[2].text = fog_attrs["blue"]

        # Modify .foganim.xml
        # 1. startDistanceKeyframes
        for ele in fa_root.iter("startDistanceKeyframes"):
            ele[0][2].text = fog_attrs["start"]
            ele[1][2].text = fog_attrs["start"]

        # 2. endDistanceKeyframes
        for ele in fa_root.iter("endDistanceKeyframes"):
            ele[0][2].text = fog_attrs["end"]
            ele[1][2].text = fog_attrs["end"]

        # 3. redKeyframes
        for ele in fa_root.iter("redKeyframes"):
            ele[0][2].text = fog_attrs["red"]
            ele[1][2].text = fog_attrs["red"]

        # 4. greenKeyframes
        for ele in fa_root.iter("greenKeyframes"):
            ele[0][2].text = fog_attrs["green"]
            ele[1][2].text = fog_attrs["green"]

        # 5. blueKeyframes
        for ele in fa_root.iter("blueKeyframes"):
            ele[0][2].text = fog_attrs["blue"]
            ele[1][2].text = fog_attrs["blue"]

        f_tree.write(fog, xml_declaration=True)
        fa_tree.write(fog_anim, xml_declaration=True)

    def copy_fog_xml():
        """
        Executes SMBFogTool's copy-fog-xml-to-stage-def function
        :return: None
        """

        if not os.path.isfile(lzraw):
            print("\n{} not found. Quitting program...".format(lzraw))
            sys.exit()
        while True:
            fog_path = input("\nEnter path to .fog.xml and .foganim.xml files including shared file name (ex:"
                             " 'water' for water.fog.xml, water.foganim.xml): ")
            if not os.path.isfile("{}.fog.xml".format(fog_path))\
                    and not os.path.isfile("{}.foganim.xml".format(fog_path)):
                print("\n{}.fog.xml and {}.foganim.xml not found.".format(fog_path, fog_path))

            elif not os.path.isfile("{}.fog.xml".format(fog_path)):
                print("\n{}.fog.xml not found.".format(fog_path))

            elif not os.path.isfile("{}.foganim.xml".format(fog_path)):
                print("\n{}.foganim.xml not found.".format(fog_path))

            else:
                break

        subprocess.call([fog_tool_executable, "-i", lzraw, "-c", fog_path])
        os.remove(lzraw)
        os.rename("{}.out".format(lzraw), lzraw)

    def copy_fog_sd():
        """
        Executes SMBFogTool's function that copies fog data from stage
        def to another stage def
        :return: None
        """
        if not os.path.isfile(os.path.join(stage_dir, raw_lz_file)):
            print("Destination (output.lz.raw) not found in {}. Quitting program...".format(stage_dir))
            sys.exit(1)

        target_sd = os.path.join(stage_dir, raw_lz_file)
        while True:
            source_sd = input("\nEnter source .lz.raw path (the stage def that you want to copy fog data from): ")
            if not os.path.isfile(source_sd):
                print("\nSource .lz.raw not found.")
            else:
                break

        subprocess.call([fog_tool_executable, "-i", source_sd, "-o", target_sd])
        os.remove(lzraw)
        os.rename("{}.out".format(lzraw), lzraw)

    def sd_extract():
        """
        Executes SMBFogTool functionality - extract fog from stagedef
        :return:
        """
        while True:
            sd_dir = input("\nEnter stagedef directory: ")
            if not os.path.isdir(sd_dir):
                print("\nInvalid directory.")
            else:
                sd = get_file(sd_dir, ".raw")
                if not sd:
                    print("\nstagedef not found.")
                else:
                    sd_path = os.path.join(sd_dir, sd)
                    break

        subprocess.call([fog_tool_executable, "-i", sd_path])

    while True:
        sub_func = input("\n1 ---> Edit fog xml (color, type, boundaries)\n"
                         "2 ---> Copy fog data from xml to stagedef\n"
                         "3 ---> Copy fog data from source stagedef to destination stagedef\n"
                         "4 ---> Extract fog data from stagedef to xml\n"
                         "Enter command: ")

        if sub_func != '1' and sub_func != '2' and sub_func != '3' and sub_func != '4':
            print("\nInvalid input.")
            continue

        elif sub_func == '1':
            edit_fog_xml()
        elif sub_func == '2':
            copy_fog_xml()
        elif sub_func == '3':
            copy_fog_sd()
        elif sub_func == '4':
            sd_extract()
        break


def comp_lz(s_name, s_number, stages_dir, lz_tool_dir):
    """
    Run lz_both.bat file with the following command line arguments (in order):
        (1) SMB_LZ_Tool directory, (2) stages directory, (3) stage name

    :param s_name: Stage name
    :param s_number: Stage number
    :param lz_tool_dir: Directory containing SMB_LZ_Tool.exe file
    :param stages_dir: Directory of stage folders
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    raw_lz_file = "output.lz.raw"

    # Check if output.lz.raw file exists in stage_dir
    if not os.path.isfile(os.path.join(stage_dir, raw_lz_file)):
        print("{} does not exist in {}. Quitting program...".format(raw_lz_file, stage_dir))
        sys.exit(1)

    subprocess.call(["lz.bat", lz_tool_dir, stages_dir, s_name])
    os.remove(os.path.join(stage_dir, "output.lz.raw"))

    src = os.path.join(stage_dir, "output.lz.raw.lz")
    dst = os.path.join(stage_dir, "STAGE{}.lz".format(s_number))
    if os.path.isfile(dst):
        os.remove(dst)
    os.rename(src, dst)


def gmatpl(s_name, s_number, stages_dir, gx_dir, gxnogui_dir, in_xml=None):
    """
    Run GXModelViewer or GXModelViewerNoGUI

    :param s_name: Stage name passed in from stage_name function
    :param s_number: Stage number passed in from stage number function
    :param stages_dir: Directory of stage folders
    :param gx_dir: Directory of GXModelViewer.exe
    :param gxnogui_dir: Directory of GXModelViewer.exe (NOGUI)
    :param in_xml: xml file name if LZ was created in the same code run; Else, None
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    gx_dir = os.path.expanduser(gx_dir)
    gxnogui_dir = os.path.expanduser(gxnogui_dir)
    gx_executable = os.path.join(gx_dir, "GxModelViewer.exe")
    gxnogui_executable = os.path.join(gxnogui_dir, "GxModelViewer.exe")

    if in_xml:
        xml_file = in_xml
    else:
        xml_file = get_file(stage_dir, ".xml")

    obj_file = get_obj(os.path.join(stage_dir, xml_file))
    obj_file_w_path = os.path.join(stage_dir, obj_file)
    obj_file_no_ext = obj_file.split(".")[0]

    src_gma = os.path.join(stage_dir, "{}.gma".format(obj_file_no_ext))
    src_tpl = os.path.join(stage_dir, "{}.tpl".format(obj_file_no_ext))
    dst_gma = os.path.join(stage_dir, "st{}.gma".format(s_number))
    dst_tpl = os.path.join(stage_dir, "st{}.tpl".format(s_number))

    while True:
        gui_choice = input("Open GX with or without GUI? (Y for GUI, N for NOGUI) ")
        if gui_choice == "":
            subprocess.call([gxnogui_executable, obj_file_w_path])

            if not os.path.isfile(src_gma) or not os.path.isfile(src_tpl):
                print("{}.gma and/or {}.tpl files not found. "
                      "Quitting program...".format(obj_file_no_ext, obj_file_no_ext))
                sys.exit(1)
            break

        elif gui_choice.lower()[0] == "n":
            subprocess.call([gxnogui_executable, obj_file_w_path])

            if not os.path.isfile(src_gma) or not os.path.isfile(src_tpl):
                print("{}.gma and/or {}.tpl files not found. "
                      "Quitting program...".format(obj_file_no_ext, obj_file_no_ext))
                sys.exit(1)
            break

        elif gui_choice.lower()[0] == "y":
            os.startfile(gx_executable)
            print("Opening GXModelViewer...")
            time.sleep(5)
            input("Enter anything when done using GXModelViewer. ").lower()

            while True:
                if not os.path.isfile(dst_gma) or not os.path.isfile(dst_tpl):
                    input("st{}.gma and/or st{}.tpl files not found. Enter anything when both files "
                          "are in {} ".format(stg_number, stg_number, stage_dir))
                else:
                    break

            break

        else:
            print("Invalid input! Try again.")

    if os.path.isfile(src_gma) and os.path.isfile(src_gma):
        if os.path.isfile(dst_gma):
            os.remove(dst_gma)
            os.rename(src_gma, dst_gma)
        else:
            os.rename(src_gma, dst_gma)

        if os.path.isfile(dst_tpl):
            os.remove(dst_tpl)
            os.rename(src_tpl, dst_tpl)
        else:
            os.rename(src_tpl, dst_tpl)
    else:
        pass


def use_gmatool(s_name, s_number, stages_dir, gmatool_dir):
    """

    :param s_name: Stage name
    :param s_number: Stage number
    :param stages_dir: Directory of stage folders
    :param gmatool_dir: gmatool.exe directory
    :return: None
    """

    while True:
        merge_input = input("Use gmatool to merge files? (Y/N) ").lower()
        if not merge_input or merge_input != "y" and merge_input != "n":
            print("Invalid input.")
        elif merge_input == "n":
            break
        else:

            stages_dir = os.path.expanduser(stages_dir)
            stage_dir = os.path.join(stages_dir, s_name)
            stage_gmatpl = os.path.join(stage_dir, "st{}".format(s_number))

            #   Input source models

            source_files = [stage_gmatpl]   # list of all model file paths (WITHOUT extensions) starting with the
            # stage model path
            source_models = [os.path.split(stage_gmatpl)[-1]]  # list of all model names. List starts with stage model
            files = 1
            while files < 2:
                i_gmatpl = input("Enter path (WITHOUT file extension) to GMA/TPL to be merged with {}. If model"
                                 " is in {}, just provide the name of the file. ".format(stage_gmatpl, gmatool_dir))

                #   If input is just a filename and these files both exist in gmatool.exe directory, add that path to
                #   file

                gt_path_gma = os.path.join(gmatool_dir, "{}.gma".format(i_gmatpl))
                gt_path_tpl = os.path.join(gmatool_dir, "{}.tpl".format(i_gmatpl))

                if os.path.isfile(gt_path_gma) and os.path.isfile(gt_path_tpl):
                    i_gmatpl = os.path.join(gmatool_dir, i_gmatpl)
                elif not os.path.isfile(gt_path_gma) and os.path.isfile(gt_path_tpl):
                    print("\n{} not found.\n".format(gt_path_gma))
                    continue
                elif not os.path.isfile(gt_path_tpl) and os.path.isfile(gt_path_gma):
                    print("\n{} not found.\n".format(gt_path_tpl))
                    continue
                else:
                    print("\n{} and {} not found.\n".format(gt_path_gma, gt_path_tpl))
                    continue

                if i_gmatpl in source_files:
                    print("\nDuplicate file. Try again.\n")
                    continue
                elif not os.path.isfile("{}.gma".format(i_gmatpl)) or not os.path.isfile("{}.tpl".format(i_gmatpl)):
                    print("{}.gma and/or {}.tpl not found.\n".format(i_gmatpl, i_gmatpl))
                    continue
                else:
                    model = os.path.split(i_gmatpl)[-1]
                    source_files.append(i_gmatpl)
                    source_models.append(model)
                    files += 1

                    if files >= 2:
                        while True:
                            add_file = input("Add another GMA/TPL? (Y/N): ").lower()

                            if not add_file or add_file != "y" and add_file != "n":
                                print("Invalid input.")
                                continue
                            elif add_file == "n":
                                break
                            else:
                                i_gmatpl = input("GMA/TPL path ({}) WITHOUT file extension: ".format(files + 1))

                                gt_path_gma = os.path.join(gmatool_dir, "{}.gma".format(i_gmatpl))
                                gt_path_tpl = os.path.join(gmatool_dir, "{}.tpl".format(i_gmatpl))

                                if os.path.isfile(gt_path_gma) and os.path.isfile(gt_path_tpl):
                                    i_gmatpl = os.path.join(gmatool_dir, i_gmatpl)
                                elif not os.path.isfile(gt_path_gma) and os.path.isfile(gt_path_tpl):
                                    print("\n{} not found.\n".format(gt_path_gma))
                                    continue
                                elif not os.path.isfile(gt_path_tpl) and os.path.isfile(gt_path_gma):
                                    print("\n{} not found.\n".format(gt_path_tpl))
                                    continue
                                else:
                                    print("\n{} and {} not found.\n".format(gt_path_gma, gt_path_tpl))
                                    continue

                                if i_gmatpl in source_files:
                                    print("Duplicate file. Try again.")
                                    continue

                                else:
                                    model = os.path.split(i_gmatpl)[-1]
                                    source_files.append(i_gmatpl)
                                    source_models.append(model)
                                    files += 1

            #   Move all models to gmatool directory if they do not already exist in that directory

            trash_files = []
            for model_path in source_files:
                model = os.path.split(model_path)[-1]
                src_gma = os.path.join("{}.gma".format(model_path))
                src_tpl = os.path.join("{}.tpl".format(model_path))
                dst_gma = os.path.join(gmatool_dir, "{}.gma".format(model))
                dst_tpl = os.path.join(gmatool_dir, "{}.tpl".format(model))

                if not os.path.isfile(dst_gma):
                    shutil.copyfile(src_gma, dst_gma)
                    trash_files.append(dst_gma)

                elif src_gma != dst_gma:
                    os.remove(dst_gma)
                    shutil.copyfile(src_gma, dst_gma)
                    trash_files.append(dst_gma)

                else:
                    pass

                if not os.path.isfile(dst_tpl):
                    shutil.copyfile(src_tpl, dst_tpl)
                    trash_files.append(dst_tpl)

                elif src_tpl != dst_tpl:
                    os.remove(dst_tpl)
                    shutil.copyfile(src_tpl, dst_tpl)
                    trash_files.append(dst_tpl)

                else:
                    pass

            #   Merge all files together

            os.chdir(gmatool_dir)
            combined_model = ""
            while len(source_models) > 1:
                model_1 = source_models[0]
                model_2 = source_models[1]
                subprocess.call(["gmatool.exe", "-m", model_1, model_2])

                #   Delete previous combined model
                if combined_model:
                    os.remove("{}.gma".format(combined_model))
                    os.remove("{}.tpl".format(combined_model))

                combined_model = "{}+{}".format(model_1, model_2)

                source_models.remove(model_1)
                source_models.remove(model_2)
                source_models.insert(0, combined_model)

            src_gma = "{}.gma".format(combined_model)
            src_tpl = "{}.tpl".format(combined_model)
            dst_gma = os.path.join(stage_dir, "st{}.gma".format(s_number))
            dst_tpl = os.path.join(stage_dir, "st{}.tpl".format(s_number))

            #   Delete obsolete stage gma/tpl
            if os.path.isfile(dst_gma):
                os.remove(dst_gma)
            if os.path.isfile(dst_tpl):
                os.remove(dst_tpl)

            #   Rename new gma/tpl and move to destination
            os.rename(src_gma, dst_gma)
            os.rename(src_tpl, dst_tpl)

            #   Remove files that were moved to gmatool.exe directory from other directories
            for f in trash_files:
                os.remove(f)

            os.chdir(config_writer.tool_path)
            break


def edit_str(s_name, s_number, root):
    """
    Replaces stage name slot in usa.str
    :return: None
    """

    s_name = re.sub('_', ' ', s_name)
    str_file = os.path.expanduser(os.path.join(root, "stgname", "usa.str"))
    with open(str_file, 'r') as in_file:
        stg_names = in_file.readlines()

    stg_names[int(s_number)] = "{}\n".format(s_name)
    with open(str_file, 'w') as out_file:
        out_file.writelines(stg_names)


def replace_stage_files(s_name, s_number, stages_dir, root):
    """
    Copies stage files from //<stagename> folder to //stages folder in ISO
    if and only if all three stage files (STAGEXXX.lz, stXXX.gma, stXXX.gma) exist in //<stagename>.

    :param s_name: Stage name passed in from stage_name function
    :param s_number: Stage number passed in from stage_number function
    :param stages_dir: Directory of stage folders
    :param root: ISO root folder path
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    iso_stages_dir = os.path.expanduser(os.path.join(root, "stage"))

    src_lz = os.path.join(stage_dir, "STAGE{}.lz".format(s_number))
    src_gma = os.path.join(stage_dir, "st{}.gma".format(s_number))
    src_tpl = os.path.join(stage_dir, "st{}.tpl".format(s_number))
    missing_files = []

    if not os.path.isfile(src_lz):
        missing_files.append("STAGE{}.lz".format(s_number))

    if not os.path.isfile(src_gma):
        missing_files.append("st{}.gma".format(s_number))

    if not os.path.isfile(src_tpl):
        missing_files.append("st{}.tpl".format(s_number))

    if len(missing_files) != 0:
        missing_files_str = ", ".join([file for file in missing_files])
        print("\nMissing files from {}: {}".format(stage_dir, missing_files_str))
        print("Cannot replace stage files.")
        print("Quitting program...")
        sys.exit(1)

    dst_lz = os.path.join(iso_stages_dir, "STAGE{}.lz".format(s_number))
    dst_gma = os.path.join(iso_stages_dir, "st{}.gma".format(s_number))
    dst_tpl = os.path.join(iso_stages_dir, "st{}.tpl".format(s_number))

    shutil.copyfile(src_lz, dst_lz)
    shutil.copyfile(src_gma, dst_gma)
    shutil.copyfile(src_tpl, dst_tpl)


def rebuild_iso(gcr_dir, iso_dir):
    """
    Run gcr.exe

    Must type either "Y" or "y" to open GCR
    :param gcr_dir: Directory of gcr.exe file
    :param iso_dir: Directory of ISO disc file
    :return: None
    """
    gcr_dir = os.path.expanduser(gcr_dir)
    gcr_executable = os.path.join(gcr_dir, "gcr.exe")
    iso_file = get_file(iso_dir, ".iso", override=True)

    iso_file_path = os.path.join(iso_dir, iso_file)
    root_dir = os.path.join(iso_dir, "files")

    print("\nRebuilding ISO...\n")
    subprocess.call([gcr_executable, root_dir, iso_file_path])
    print("DONE!")


def playtest(dol_executable, md_path):
    """

    :param dol_executable: Dolphin.exe path
    :param md_path: main.dol path
    :return: None
    """
    dol_executable = os.path.join(dol_executable, "Dolphin.exe")
    md_path = os.path.join(md_path, "main.dol")

    while True:
        exec_option = input("Render game in Dolphin with or without GUI? (Y -> GUI, N -> No GUI) ").lower()
        if exec_option != 'y' and exec_option != 'n':
            print("\nInvalid input.\n")
        elif exec_option == 'y':
            subprocess.call([dol_executable, '-e', md_path])
            break
        else:
            subprocess.call([dol_executable, '--batch', md_path])
            break


def select_cmd():
    """
    User selects a command (key) in help_dict

    :return: User-specified command
    """
    help_dict = {'1': "Create LZ, GMA/TPL, "
                      "replace stage files in <ISO path>//stage directory, playtest game",
                 '2': "Create LZ, GMA/TPL, "
                      "replace stage files in <ISO path>//stage directory",
                 '3': "Create LZ, GMA/TPL",
                 '4': "Create .lz.raw, use SMBFogTool",
                 '5': "Compress .lz.raw",
                 '6': "Create LZ",
                 '7': "Create GMA/TPL",
                 '8': "Replace stage files in <ISO path>//stage directory",
                 '9': "Playtest game",
                 '10': "Rebuild ISO"
                 }

    for h_key, h_value in help_dict.items():
        print("{} ----> {}".format(h_key, h_value))

    while True:
        cmd_input = input("\nEnter command: ")
        if cmd_input == "":
            print("\nInvalid command! Try again.")

        elif cmd_input.lower() not in help_dict.keys():
            print("\nInvalid command! Try again.")

        else:
            return cmd_input.lower()


if __name__ == '__main__':

    stage_dir = cl_dict["stage_dir"]
    stage_index = cl_dict["index"]

    # if type(stage_dir) == str and type(stage_index) == int:
    #     if function requires stage_dir and stage_index:
    #         execute function
    #     elif function doesn't require stage_dir and/or stage_index:
    #         still execute function
    #
    # elif type(stage_dir) == str (as in type(stage_index) == None):
    #     if function requires stage_dir and stage_index:
    #         produce error message, quit program
    #     elif function requires stage_index:
    #         produce error message, quit program
    #     elif function requires stage_dir:
    #         execute function
    #     elif function doesn't require neither stage_dir nor stage_index:
    #         execute function
    #
    # elif stage_index == int (as in type(stage_dir) == None):
    #     if function requires stage_dir and stage_index:
    #         produce error message, quit program
    #     elif function requires stage_dir:
    #         produce error message, quit program
    #     elif function requires stage_index:
    #         execute function
    #     elif function doesn't require neither stage_dir nor stage_index:
    #         execute function
    #
    # else (as in type(stage_dir) == None, type(stage_index) == None):
    #     execute function

    """
    if arg == '1':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()

        x = stage_def_to_lz(stg_name, stg_number, paths.levels,
                            paths.ws2ify, paths.ws2, paths.smb_lz_tool, return_xml=True)

        gmatpl(stg_name, stg_number, paths.levels, paths.gxmodelviewer, paths.gxmodelviewernogui, in_xml=x)
        use_gmatool(stg_name, stg_number, paths.levels, paths.gmatool)
        replace_stage_files(stg_name, stg_number, paths.levels, paths.root)
        edit_str(stg_name, stg_number, paths.root)
        playtest(paths.dolphin, paths.playtest)
        del stg_name, stg_number, x

    elif arg == '2':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()

        x = stage_def_to_lz(stg_name, stg_number, paths.levels,
                            paths.ws2ify, paths.ws2, paths.smb_lz_tool, return_xml=True)

        gmatpl(stg_name, stg_number, paths.levels, paths.gxmodelviewer, paths.gxmodelviewernogui, in_xml=x)
        use_gmatool(stg_name, stg_number, paths.levels, paths.gmatool)
        replace_stage_files(stg_name, stg_number, paths.levels, paths.root)
        edit_str(stg_name, stg_number, paths.root)
        del stg_name, stg_number, x

    elif arg == '3':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()

        x = stage_def_to_lz(stg_name, stg_number, paths.levels,
                            paths.ws2ify, paths.ws2, paths.smb_lz_tool, return_xml=True)

        gmatpl(stg_name, stg_number, paths.levels, paths.gxmodelviewer, paths.gxmodelviewernogui, in_xml=x)
        use_gmatool(stg_name, stg_number, paths.levels, paths.gmatool)
        del stg_name, stg_number, x

    elif arg == '4':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()
        stage_def(stg_name, paths.levels, paths.ws2ify, paths.ws2, paths.bgtool)
        fog_ops(stg_name, paths.levels, paths.smb_fog_tool)
        del stg_name, stg_number

    elif arg == '5':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()
        comp_lz(stg_name, stg_number, paths.levels, paths.smb_lz_tool)
        del stg_name, stg_number

    elif arg == '6':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()
        stage_def_to_lz(stg_name, stg_number, paths.levels,
                        paths.ws2ify, paths.ws2, paths.smb_lz_tool)
        del stg_name, stg_number

    elif arg == '7':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()
        gmatpl(stg_name, stg_number, paths.levels, paths.gxmodelviewer, paths.gxmodelviewernogui)
        use_gmatool(stg_name, stg_number, paths.levels, paths.gmatool)
        del stg_name, stg_number

    elif arg == '8':
        stg_name = stage_name(paths.levels)
        stg_number = stage_num()
        replace_stage_files(stg_name, stg_number, paths.levels, paths.root)
        edit_str(stg_name, stg_number, paths.root)
        del stg_name, stg_number

    elif arg == '9':
        playtest(paths.dolphin, paths.playtest)

    elif arg == '10':
        rebuild_iso(paths.gcr, paths.iso)
    """
