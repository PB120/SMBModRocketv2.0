import configparser
import sys
import os
from datetime import datetime

config = configparser.ConfigParser()
parser = configparser.ConfigParser()
tool_path = sys.path[0]
config_filename = "config.ini"
edit_date_checker = "last_edited.txt"


def config_init():
    """

    :return: dictionary: keys are names relevant to specific file/folder path/directory.
    Values are lists containing short descriptions about the file/folder path/directory
    and may contain flags. The flags are files/folders that are required to exist in a specific path/directory
    in setup_config(). If there is one flag, it will exist in the list as a STRING.
    If more than one flag exists, these will exist in the list as a SUBLIST of strings.
    """

    config_dict = {"Your levels": ["Path to folder containing subfolders which are names of your levels: "],
                   "ws2": ["ws2lzfrontend.exe directory: ", "ws2lzfrontend.exe"],
                   "ws2ify": ["ws2ify path: ", "run.py"],
                   "bgtool": ["bgtool.exe directory: ", "bgtool.exe"],
                   "SMBFogTool": ["SMBFogTool.exe directory: ", "SMBFogTool.exe"],
                   "SMB_LZ_Tool": ["SMB_LZ_Tool path: ", "SMB_LZ_Tool.exe"],
                   "gmatool": ["gmatool.exe directory: ", "gmatool.exe"],
                   "GXModelViewer": ["GXModelViewer path: ", "GXModelViewer.exe"],
                   "GxModelViewerNoGUI": ["GxModelViewerNoGUI path: ", "GXModelViewer.exe"],
                   "ISO": ["<gamefilename>.iso directory: ", ["root", ".iso"]],
                   "GCR": ["gcr.exe directory: ", "gcr.exe"]
                   }

    return config_dict


def setup_config():
    """

    :return: dict
    """

    while True:

        new_config_dict = {}

        def flag_0(val):
            """
            Check if inputted directory/path exists (No flags)
            :param val: value from config_init
            :return: directory/path from user input
            """
            while True:
                user_input = os.path.expanduser(input(val[0]))

                # Check if inputted directory/path exists

                if not os.path.isdir(user_input):
                    print("Invalid path.")
                    continue
                else:
                    break
            return user_input

        def flag_1(val, flag):
            """
            Check if inputted directory/path exists (1 flag)
            :param val: value from config_init dict
            :param flag: file/folder that should exist in user inputted directory (str)
            :return: directory/path from user input
            """
            while True:
                user_input = os.path.expanduser(input(val[0]))

                # Check if inputted directory/path exists

                if not os.path.isdir(user_input):
                    print("Invalid path.")
                else:
                    path_w_flag = os.path.join(user_input, flag)
                    all_files = os.listdir(user_input)
                    flag_found = False
                    for f in all_files:
                        if f.endswith(flag):
                            flag_found = True

                    # Check if file/folder/file extension flag exists in user inputted path/directory

                    if not os.path.isdir(path_w_flag) and not os.path.isfile(path_w_flag) and not flag_found:
                        print("Missing file/folder/file extension: {}".format(flag))
                    else:
                        break

            return user_input

        def flag_m(val, flag_list):
            """
            Check if inputted directory/path exists (2 or more flags)
            :param val: value from config_init dict
            :param flag_list: files/folders that should exist in user inputted directory (list)
            :return: directory/path from user input
            :return:
            """
            while True:
                user_input = os.path.expanduser(input(val[0]))

                # Check if inputted directory/path exists

                if not os.path.isdir(user_input):
                    print("Invalid path.")
                else:
                    break

            while True:
                missing_flags = []
                for flag in flag_list:
                    flag_found = False
                    all_files = os.listdir(user_input)

                    for f in all_files:
                        if f.endswith(flag):
                            flag_found = True

                    if not flag_found:
                        missing_flags.append(flag)

                if missing_flags:

                    [print("File/file extension/folder \"{}\" not found.".format(flag)) for flag in missing_flags]
                    while True:
                        user_input = input("Re-enter path/directory: ")
                        if not os.path.isdir(user_input):
                            print("Invalid input.")
                        else:
                            break

                else:
                    break

            return user_input

        for k, v in config_init().items():

            if len(v) == 1:
                entry = flag_0(v)
                new_config_dict[k] = entry

            elif len(v) == 2 and type(v[1]) == str:

                entry = flag_1(v, v[1])
                new_config_dict[k] = entry

            elif len(v) == 2 and type(v[1]) == list:

                entry = flag_m(v, v[1])
                new_config_dict[k] = entry

        print("\nYour entries: \n")
        [print("{}:".format(k), v) for k, v in new_config_dict.items()]

        while True:
            redo_setup = input("\nWrite config? (Y if your entries are all correct, N if you want to redo them): ")
            if redo_setup.lower() != 'y' and redo_setup.lower() != 'n':
                print("Invalid input.")
            elif redo_setup.lower() == 'n':
                break
            else:
                return new_config_dict


def modified():
    """

    :return: int 0 if config file exists and no changes have been made to the file,
             int 1 if config file exists and was recently updated,
             int -1 if config file does not exist
    """
    if os.path.isfile(config_filename):
        actual_date = str(datetime.fromtimestamp(os.stat(config_filename).st_mtime))
        with open(edit_date_checker, 'r') as edc_read:
            date_from_file = edc_read.readline()
        if date_from_file != actual_date:
            return 1
        else:
            return 0

    else:
        return -1


print(modified())
sys.exit()
config["Last Modified"] = {"datetime": date_modified}
config["Paths/directories"] = setup_config()
print(config.sections())
sys.exit()

if modified() == 1:
    while True:
        user_choice = input("{} has been modified outside of program. Continue anyway? (Y/N) ").lower()
        if not user_choice or user_choice != 'n' and user_choice != 'y':
            print("Invalid input.")
        elif user_choice == 'n':
            sys.exit()
        else:
            break

elif modified() == 0:
    pass

elif modified() == -1:
    config["Paths/directories"] = setup_config()
    with open(config_filename, 'w') as config_file:
        config.write(config_file)

parser.read(config_filename)


class Paths(object):

    def __init__(self, your_levels, ws2, ws2ify, bgtool, smb_fog_tool, smb_lz_tool, gmatool, gxmodelviewer,
                 gxmodelviewernogui, iso, gcr):

        self.your_levels = your_levels
        self.ws2 = ws2
        self.ws2ify = ws2ify
        self.bgtool = bgtool
        self.smb_fog_tool = smb_fog_tool
        self.smb_lz_tool = smb_lz_tool
        self.gmatool = gmatool
        self.gxmodelviewer = gxmodelviewer
        self.gxmodelviewernogui = gxmodelviewernogui
        self.iso = iso
        self.gcr = gcr


paths = Paths(parser.get("Paths/directories", "Your levels"),
              parser.get("Paths/directories", "ws2"),
              parser.get("Paths/directories", "ws2ify"),
              parser.get("Paths/directories", "bgtool"),
              parser.get("Paths/directories", "SMBFogTool"),
              parser.get("Paths/directories", "SMB_LZ_Tool"),
              parser.get("Paths/directories", "gmatool"),
              parser.get("Paths/directories", "gxmodelviewer"),
              parser.get("Paths/directories", "gxmodelviewernogui"),
              parser.get("Paths/directories", "iso"),
              parser.get("Paths/directories", "gcr")
              )
