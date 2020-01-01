"""Automates creation, renaming and moving of SMB stage files"""
import subprocess
import sys
import os
from shutil import copyfile
import xml.etree.ElementTree as et
import config_writer
import pdb


def get_file(path, extension):
    """
    Grab filename of a file inside a specific directory that has a specific file extension

    :param path: file path
    :param extension: file extension
    :return: File name if the number of files with specified extension >= 1.
    Else, returns None.
    """

    ext_lst = []
    for f_name in os.listdir(path):
        if f_name.endswith(extension):
            ext_lst.append(f_name)

    if len(ext_lst) == 0:
        return ext_lst

    elif len(ext_lst) == 1:
        return ext_lst[0]

    else:
        while True:
            files = [file for file in ext_lst]
            file_choice = input("\nMore than one {} file exists in {}.\n"
                                "Files available: {}\n"
                                "Please input the file name that you want. \n".format(extension, path, files))
            if file_choice in ext_lst:
                return file_choice
            else:
                print("File does not exist.")


def get_obj(xml_file):
    """
    Grabs obj filename found in xml file

    :param xml_file: xml path and file name
    :return: obj filename
    """
    file = xml_file
    tree = et.parse(file)
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
    last = 420

    while True:
        s_num = input("Enter stage number (1-420). No input will yield default 001. ")
        if s_num == "":
            s_num = "001"
            return s_num
        else:
            try:
                s_num = int(s_num)
            except ValueError:
                print("Invalid stage number! Try again.")
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

    print("\nLEVELS AVAILABLE:"
          "\n")
    stages_dir = os.path.expanduser(stages_dir)
    os.chdir(stages_dir)
    stage_lst = next(os.walk('.'))[1]
    os.chdir(config_writer.tool_path)

    for name in stage_lst:
        print(name)
    while True:
        stg_nm = input("\nEnter stage name: ")
        if stg_nm not in stage_lst:
            print("Stage name not available! Try again.")
        else:
            break

    return stg_nm


def txt_to_xml(ws2ify_path, stages_dir, s_name):
    """
    Runs ws2ify to convert txt to xml config

    :param ws2ify_path: ws2ify run.py file path
    :param stages_dir: Directory of stage folders
    :param s_name: Stage name

    :return: None
    """
    import pdb
    #pdb.set_trace()

    while True:
        use_ws2ify = input("Use ws2ify? (Y/N) ")
        use_ws2ify = use_ws2ify.upper()[0]

        if use_ws2ify != "Y" and use_ws2ify != "N":
            print("\nInvalid input.\n")
        elif use_ws2ify == "N":
            return
        else:
            break

    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)

    os.chdir(stage_dir)
    keyframe_easing_dict = {"1": "LINEAR", "2": "EASED"}
    while True:
        txt = input("Input txt filename: ")
        txt_path = os.path.join(stage_dir, txt)
        if not os.path.isfile(txt_path):
            print("\nFile not found.\n")
        else:
            break

    while True:
        obj = input("Input obj filename: ")
        obj_path = os.path.join(stage_dir, obj)
        if not os.path.isfile(obj_path):
            print("\nFile not found.\n")
        else:
            break

    while True:
        keyframe_easing = input("Keyframe easing = linear(1) or eased(2)? Enter 1 or 2: ")
        print(keyframe_easing)
        if keyframe_easing != "1" and keyframe_easing != "2":
            print("\nInvalid input.\n")
        else:
            keyframe_easing = keyframe_easing_dict[keyframe_easing]
            break

    xml = "{}.xml".format(input("Output xml filename: "))
    xml_path = os.path.join(stage_dir, xml)

    ws2ify_path = os.path.expanduser(ws2ify_path)
    os.chdir(ws2ify_path)
    print(os.path.isfile("{}/run.py".format(ws2ify_path)))
    subprocess.call(["python", "run.py", txt_path, obj_path, xml_path, keyframe_easing])
    os.chdir(config_writer.tool_path)


#txt_to_xml("F:\SMBCustomLevelStuff\ws2ify-master", "F:\SMBCustomLevelStuff\Levels", "Plane_Simple")


def stage_def_to_lz(s_name, s_number, stages_dir, ws2_fe_dir, lz_tool_dir):
    """
    Run lz_both.bat file with the following command line arguments (in order):
        (1) ws2lzfrontend.exe directory, (2) stages directory,
        (3) stage name, (4) stage xml filename, (5) SMB_LZ_Tool directory

    :param s_name: Stage name
    :param s_number: Stage number
    :param ws2_fe_dir: Directory containing ws2lzfrontend.exe file
    :param lz_tool_dir: Directory containing SMB_LZ_Tool.exe file
    :param stages_dir: Directory of stage folders
    :return: None
    """
    #pdb.set_trace()
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    xml_file = get_file(stage_dir, ".xml")

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


def stage_def(s_name, stages_dir, ws2_fe_dir):
    """
    Run lz_raw.bat file with the following command line arguments (in order):
        (1) ws2lzfrontend.exe directory, (2) stages directory,
        (3) stage name, (4) stage xml filename

    :param s_name: Stage name
    :param ws2_fe_dir: Directory containing ws2lzfrontend.exe file
    :param stages_dir: Directory of stage folders
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    xml_file = get_file(stage_dir, ".xml")
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
                sys.exit(0)
            else:
                subprocess.call(["lz_raw.bat", ws2_fe_dir, stages_dir, s_name, xml_file])
                break

    else:
        subprocess.call(["lz_raw.bat", ws2_fe_dir, stages_dir, s_name, xml_file])


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


def gmatpl(s_name, s_number, stages_dir, gx_dir, gxnogui_dir):
    """
    Run GXModelViewer or GXModelViewerNoGUI

    :param s_name: Stage name passed in from stage_name function
    :param s_number: Stage number passed in from stage_number function
    :param stages_dir: Directory of stage folders
    :param gx_dir: Directory of GXModelViewer.exe
    :param gxnogui_dir: Directory of GXModelViewer.exe (NOGUI)
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    gx_dir = os.path.expanduser(gx_dir)
    gxnogui_dir = os.path.expanduser(gxnogui_dir)
    gx_executable = os.path.join(gx_dir, "GxModelViewer.exe")
    gxnogui_executable = os.path.join(gxnogui_dir, "GxModelViewer.exe")
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
            print("Opening GXModelViewer...")
            subprocess.call([gx_executable])
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


def replace_stage_files(s_name, s_number, stages_dir, iso_stages_dir):
    """
    Copies stage files from //<stagename> folder to //stages folder in ISO
    if and only if all three stage files (STAGEXXX.lz, stXXX.gma, stXXX.gma) exist in //<stagename>.

    :param s_name: Stage name passed in from stage_name function
    :param s_number: Stage number passed in from stage_number function
    :param stages_dir: Directory of stage folders
    :param iso_stages_dir: Path of "stages" folder in game root folder
    :return: None
    """
    stages_dir = os.path.expanduser(stages_dir)
    stage_dir = os.path.join(stages_dir, s_name)
    iso_stages_dir = os.path.expanduser(iso_stages_dir)

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

    copyfile(src_lz, dst_lz)
    copyfile(src_gma, dst_gma)
    copyfile(src_tpl, dst_tpl)


def open_gcr(gcr_dir):
    """
    Run gcr.exe

    Must type either"Y" or "y" to open GCR
    :param gcr_dir: Directory of gcr.exe file
    :return: None
    """
    gcr_dir = os.path.expanduser(gcr_dir)
    gcr_executable = os.path.join(gcr_dir, "gcr.exe")
    subprocess.Popen([gcr_executable])


def select_cmd():
    """
    User selects a command (key) in help_dict

    :return: User-specified command
    """
    help_dict = {'a': "Create and compress LZ, create GMA/TPL, "
                      "replace stage files in //stage directory of ISO, run GCR",
                 'ang': "Create and compress LZ, create GMA/TPL, "
                        "replace stage files in //stage directory of ISO",
                 'anr': "Create and compress LZ, create GMA/TPL",
                 'ra': "Create .lz.raw file",
                 'cp': "Compress .lz.raw file",
                 'rc': "Create .lz.raw file, compress .lz.raw file",
                 'gt': "Create GMA/TPL",
                 'rs': "Replace stage files in //stage directory of ISO, run GCR",
                 'gc': "Run GCR"
                 }

    print("\nCommands:\n")
    for h_key, h_value in help_dict.items():
        print("{} ----> {}".format(h_key, h_value))

    while True:
        cmd_input = input("\nEnter command: ")
        if cmd_input == "":
            print("Invalid command! Try again.")

        elif cmd_input.lower() not in help_dict.keys():
            print("Invalid command! Try again.")

        else:
            return cmd_input.lower()


if __name__ == '__main__':

    # Run config_writer.py
    config_writer

    dirs = config_writer.grab_dirs()
    incorrect_dir = False
    for key, value in dirs.items():
        if not os.path.isdir(value):
            print("\"{}\" is not a valid directory for {}!".format(value, key))
            incorrect_dir = True
    if incorrect_dir:
        print("Quitting program...")
        sys.exit(1)

    cmd = select_cmd()
    if cmd == 'a':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()

        stage_def_to_lz(stage_name, stage_number, dirs["levels"], dirs["ws2lzfrontend"], dirs["SMB_LZ_Tool"])

        gmatpl(stage_name, stage_number, dirs["levels"], dirs["GXModelViewer"], dirs["GxModelViewerNoGUI"])
        replace_stage_files(stage_name, stage_number, dirs["levels"], dirs["stage"])
        open_gcr(dirs["gcr"])

    elif cmd == 'ang':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        stage_def_to_lz(stage_name, stage_number, dirs["levels"], dirs["ws2lzfrontend"], dirs["SMB_LZ_Tool"])
        gmatpl(stage_name, stage_number, dirs["levels"], dirs["GXModelViewer"], dirs["GxModelViewerNoGUI"])
        replace_stage_files(stage_name, stage_number, dirs["levels"], dirs["stage"])

    elif cmd == 'anr':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        stage_def_to_lz(stage_name, stage_number, dirs["levels"], dirs["ws2lzfrontend"], dirs["SMB_LZ_Tool"])
        gmatpl(stage_name, stage_number, dirs["levels"], dirs["GXModelViewer"], dirs["GxModelViewerNoGUI"])

    elif cmd == 'ra':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        stage_def(stage_name, dirs["levels"], dirs["ws2lzfrontend"])

    elif cmd == 'cp':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        comp_lz(stage_name, stage_number, dirs["levels"], dirs["SMB_LZ_Tool"])

    elif cmd == 'rc':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        stage_def_to_lz(stage_name, stage_number, dirs["levels"], dirs["ws2lzfrontend"], dirs["SMB_LZ_Tool"])

    elif cmd == 'gt':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        gmatpl(stage_name, stage_number, dirs["levels"], dirs["GXModelViewer"], dirs["GxModelViewerNoGUI"])

    elif cmd == 'rs':
        stage_name = stage_name(dirs["levels"])
        stage_number = stage_num()
        replace_stage_files(stage_name, stage_number, dirs["levels"], dirs["stage"])

    elif cmd == 'gc':
        open_gcr(dirs["gcr"])

    else:
        print("Problem with select_cmd function. Please double check the code.")
        sys.exit(1)
