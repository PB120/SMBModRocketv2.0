"""Creates a new config file"""

import os
import sys
import glob
tool_path = sys.path[0]
filename = os.path.join(tool_path, "config.txt")
file_lst = ["ws2lzfrontend.exe", "SMB_LZ_Tool.exe", "GxModelViewer.exe", "GxModelViewer.exe", "gcr.exe"]


def grab_dirs(config_file=filename):
    """
    Grabs the directories given in config file

    :param config_file: Automation tool config file name and path (str)
    :return: Dictionary (keys as generic names describing directories: values as the directories)
    """

    dir_dict = {}

    # Return None if config file doesn't exist
    if not os.path.isfile(config_file):
        return dir_dict

    with open(config_file) as f_in:
        lines = f_in.read().splitlines()
        start_index = lines.index("YOUR DIRECTORIES")
        for ele in range(start_index + 1):
            lines.pop(0)
        for line in lines:
            dir_name = line.split("=")[0]
            dir_str = line.split("=")[1].split("\"")[1]
            dir_dict[dir_name] = dir_str

    return dir_dict


def default_config(f_name):
    """
    Generates a default config file
    :param f_name: config file name
    :return: Nothing
    """
    with open(f_name, "w+") as f_out:
        f_out.write("Directory descriptions\n"
                    "levels: Directory of your custom SMB2 level folders\n"
                    "ws2lzfrontend: Directory of ws2lzfrontend.exe\n"
                    "ws2ify: Directory of ws2ify run.py file\n"
                    "SMB_LZ_Tool: Directory of SMB_LZ_Tool.exe\n"
                    "GXModelViewer: Directory of GxModelViewer.exe\n"
                    "GxModelViewerNoGUI: Directory of GxModelViewer.exe (NOGUI)\n"
                    "stage: Directory of \"stage\" folder in game root folder\n"
                    "gcr: Directory of gcr.exe\n"
                    "\n"
                    "YOUR DIRECTORIES\n"
                    "levels=\"Enter your directory here\"\n"
                    "ws2lzfrontend=\"Enter your directory here\"\n"
                    "ws2ify=\Enter your directory here\"\n"
                    "SMB_LZ_Tool=\"Enter your directory here\"\n"
                    "GXModelViewer=\"Enter your directory here\"\n"
                    "GxModelViewerNoGUI=\"Enter your directory here\"\n"
                    "stage=\"Enter your directory here\"\n"
                    "gcr=\"Enter your directory here\"\n"
                    )


def map_files(f_lst, dirs_dict):
    """

    :param f_lst: list of files
    :param dirs_dict: Dictionary (keys as generic names describing directories: values as directories)
    :return: Dictionary (keys as generic names describing directories: values as either file names or "")
    """
    file_dict = {}
    for key in dirs_dict.keys():
        file_count = 0
        for file in f_lst:
            key_no_paren = key.split("(")[0]
            if key_no_paren.lower() in file.lower() or file.lower().split('.')[0] in key_no_paren.lower():
                file_dict[key] = file
                file_count += 1
        if file_count == 0:
            file_dict[key] = ""
    return file_dict


def config_input(m_files):
    """
    :param m_files: dictionary returned by map_files function
    :return: Dictionary (keys as generic names describing directories: values as the directories)
    """

    def dir_case_sensitive(path):
        """

        :param path: File/folder path
        :return: Case-sensitive path (str)
        """

        dirs_list = path.split('\\')
        # disk letter
        test_path = [dirs_list[0].upper()]
        for d in dirs_list[1:]:
            test_path += ["%s[%s]" % (d[:-1], d[-1])]
        res = glob.glob('\\'.join(test_path))
        if not res:
            # File not found
            return None
        return res[0]

    while True:
        new_dict = {}
        for key, value in m_files.items():

            while True:
                if key == "levels":
                    new_dir = input("Please input the directory "
                                    "that contains all the folders of your custom stages: ")
                elif key == "stage":
                    new_dir = input("Please input the directory of the "
                                    "\"stage\" folder found in the \"root\" "
                                    "folder of your ISO: ")
                elif key == "GXModelViewer" or key == "GxModelViewerNoGUI":
                    while True:
                        new_dir = input("Please input the {} directory: ".format(key))
                        gx_path = new_dir
                        if os.path.basename(gx_path).lower() != key.lower():
                            print("Incorrect directory for {}! Try again.".format(key))
                        else:
                            break

                elif key == "ws2ify":
                    new_dir = input("Please input the directory "
                                    "that contains the run.py file for ws2ify")
                    if not os.path.isfile(os.path.join(new_dir, "run.py")):
                        print("Directory does not contain run.py. Try again.")
                        continue

                else:
                    new_dir = input("Please input the {} directory: ".format(key))

                # Checking for invalid file paths or directories.

                if not os.path.isdir(new_dir):
                    print("\"{}\" is not a valid {} directory! Try again.".format(new_dir, key))

                # If valid path, make sure the path is the one that has the necessary file

                elif value != "" and not os.path.isfile(os.path.join(new_dir, value)):
                    print("The file {} does not exist in {}! Try again.".format(value, new_dir))

                else:
                    new_dict[key] = dir_case_sensitive(new_dir)
                    break

        print("\n")
        for key_2, value_2 in new_dict.items():
            print("{} directory:".format(key_2), value_2)
        while True:
            confirm_setup = input("\n\nPlease double check to see if the directories you entered are correct (ABOVE).\n"
                                  "Enter Y if everything is correct, N to rewrite your directories: ")
            if confirm_setup == "":
                print("Input not recognized. Try again.")
                continue

            elif confirm_setup.lower()[0] == "y":
                return new_dict

            elif confirm_setup.lower()[0] == "n":
                break

            else:
                print("Input not recognized. Try again.")
                continue


def write_config():
    """
    Generates config file with user-specified directories

    :return: Nothing
    """

    with open(filename, "w+") as f2_out:
        f2_out.write("Directory descriptions\n"
                     "levels: Directory of your custom SMB2 level folders\n"
                     "ws2lzfrontend: Directory of ws2lzfrontend.exe\n"
                     "ws2ify: Directory of run.py file in ws2ify folder\n"
                     "SMB_LZ_Tool: Directory of SMB_LZ_Tool.exe\n"
                     "GXModelViewer: Directory of GxModelViewer.exe\n"
                     "GxModelViewerNoGUI: Directory of GxModelViewer.exe (NOGUI)\n"
                     "stage: Directory of \"stage\" folder in game root folder\n"
                     "gcr: Directory of gcr.exe\n"
                     "\n"
                     "YOUR DIRECTORIES\n")
        for k, v in config_dict.items():
            f2_out.write("{}=\"{}\"\n".format(k, v))

    print("\nConfig file successfully built.")


dirs = grab_dirs()

# If the config does not exist
if not dirs:
    default_config(filename)
    dirs = grab_dirs()
    f_dict = map_files(file_lst, dirs)
    config_dict = config_input(f_dict)
    write_config()

# If the config's directories are default values ("Enter your directory here")
elif "Enter your directory here" in dirs.values():
    default_config(filename)
    dirs = grab_dirs()
    f_dict = map_files(file_lst, dirs)
    config_dict = config_input(f_dict)
    write_config()

# If the config does exist, but >=1 directories were edited outside of the program and are incorrect
else:
    incorrect_dir = False
    for dirs_key, dirs_value in dirs.items():
        if not os.path.isdir(dirs_value):
            print("\"{}\" is not a valid directory for {}!".format(dirs_value, dirs_key))
            incorrect_dir = True

    if incorrect_dir:
        while True:
            rewrite_input = input("Errors in config file. Overwrite config? (Y/N) ")
            if rewrite_input == "":
                print("Input not recognized! Try again.")
            elif rewrite_input.lower()[0] != "y" and rewrite_input.lower()[0] != "n":
                print("Input not recognized! Try again.")
            elif rewrite_input.lower()[0] == "n":
                sys.exit(0)
            else:
                default_config(filename)
                grab_dirs()
                f_dict = map_files(file_lst, dirs)
                config_dict = config_input(f_dict)
                write_config()
                break

    if not incorrect_dir:
        if __name__ == '__main__':
            while True:
                overwrite_input = input("Config file already built! Overwrite? (Y/N) ")
                if overwrite_input == "":
                    print("Input not recognized! Try again.")
                elif overwrite_input.lower()[0] != "y" and overwrite_input.lower()[0] != "n":
                    print("Input not recognized! Try again.")
                elif overwrite_input.lower()[0] == "n":
                    sys.exit(0)
                else:
                    default_config(filename)
                    grab_dirs()
                    f_dict = map_files(file_lst, dirs)
                    config_dict = config_input(f_dict)
                    write_config()
