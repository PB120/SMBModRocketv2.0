import configparser
import sys
import os
from datetime import datetime

config = configparser.ConfigParser()
parser = configparser.ConfigParser()
tool_path = sys.path[0]
config_filename = "config.ini"
edit_date_checker = "last_edited.txt"


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


def config_init():
    """

    :return: dictionary: keys are names relevant to specific file/folder path/directory.
    Values are lists containing short descriptions about the file/folder path/directory
    and may contain flags. The flags are files/folders that are required to exist in a specific path/directory
    in setup_config(). If there is one flag, it will exist in the list as a STRING.
    If more than one flag exists, these will exist in the list as a SUBLIST of strings.
    """

    config_dict = {"Your levels": ["Path to folder containing subfolders which are names of your levels: "],
                   "ws2": ["ws2lzfrontend.exe path: ", "ws2lzfrontend.exe"],
                   "ws2ify": ["ws2ify path: ", "run.py"],
                   "bgtool": ["bgtool.exe path: ", "bgtool.exe"],
                   "SMBFogTool": ["SMBFogTool.exe path: ", "SMBFogTool.exe"],
                   "SMB_LZ_Tool": ["SMB_LZ_Tool path: ", "SMB_LZ_Tool.exe"],
                   "gmatool": ["gmatool.exe path: ", "gmatool.exe"],
                   "GXModelViewer": ["GXModelViewer path: ", "GXModelViewer.exe"],
                   "GxModelViewerNoGUI": ["GxModelViewerNoGUI path: ", "GXModelViewer.exe"],
                   "ISO": ["<gamefilename>.iso path: ", ["root", ".iso"]],
                   "GCR": ["gcr.exe path: ", "gcr.exe"]
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
    Creates last_edited.txt (if it doesn't exist) and returns an integer
    :return: int 0 if config file exists and no changes have been made to the file (date in last_edited.txt matches
    actual date of file's last modification),
             int 1 if config file exists and was recently updated (last_edited.txt does not match actual last mod date),
             int -1 if config file does not exist
    """
    # If config does not exist
    if not os.path.isfile(config_filename):
        return -1

    # Create date checking file and write in config's last modified date
    # if config exists but date checking file does not exist
    elif not os.path.isfile(edit_date_checker):
        actual_date = str(datetime.fromtimestamp(os.stat(config_filename).st_mtime))
        with open(edit_date_checker, 'w') as edc:
            edc.write(actual_date)
        return 0

    # If both files exist, compare date in edit_date_checker to config file's actual last mod date
    else:
        actual_date = str(datetime.fromtimestamp(os.stat(config_filename).st_mtime))
        with open(edit_date_checker, 'r') as edc_read:
            date_from_file = edc_read.readline()
        if date_from_file != actual_date:
            return 1
        else:
            return 0

# Test set 1

# Test 1: config file does not exist (D)
# Test 2: config file exists, date check file does not (D)
# Test 3: Both files exist (D)
    # a: date in date check file doesn't match actual mod date (D)
    # b: date in date check file matches actual mod date (D)

# Test set 2 using modified() when executing __main__

# Test 1: config file does not exist (D)
# Test 2: config file exists, date check file does not (D)
# Test 3: Both files exist (D)
    # a: date in date check file doesn't match actual mod date (D)
    # b: date in date check file matches actual mod date (D)

# Test set 2 using modified() when executing config_writer_temp.py in another python file


def date_checker():
    """
    Write in config's date last modified in last_edited file
    :return: None
    """
    with open(edit_date_checker, 'w') as edc:
        edc.write(str(datetime.fromtimestamp(os.stat(config_filename).st_mtime)))


if __name__ == '__main__':

    def exec_main_block():
        """
        Executes all functions above
        :return: None
        """

        if modified() == -1:
            config["Paths/directories"] = setup_config()
            with open(config_filename, 'w') as config_file:
                config.write(config_file)
                date_checker()

        else:
            while True:
                user_choice = input("Update config? (Y/N) ").lower()
                if not user_choice or user_choice != 'n' and user_choice != 'y':
                    print("Invalid input.")
                elif user_choice == 'n':
                    sys.exit()
                else:
                    config["Paths/directories"] = setup_config()
                    with open(config_filename, 'w') as config_file:
                        config.write(config_file)
                    date_checker()
                    break

    exec_main_block()

else:

    def exec_main_block():

        if modified() == 1:
            while True:
                user_choice = input("Config has been modified outside of program. Continue anyway? (Y/N) ").lower()
                if not user_choice or user_choice != 'n' and user_choice != 'y':
                    print("Invalid input.")
                elif user_choice == 'n':
                    sys.exit()
                else:
                    date_checker()
                    break

        elif modified() == 0:
            pass

        else:
            config["Paths/directories"] = setup_config()
            with open(config_filename, 'w') as config_file:
                config.write(config_file)
                date_checker()
