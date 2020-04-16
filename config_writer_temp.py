import configparser
import sys

config = configparser.ConfigParser()
parser = configparser.ConfigParser()

with open("config.ini", 'w') as cf:
    config.write(cf)


def config_init():
    """

    :return: dictionary: keys are names relevant to specific file/folder path
    values are lists containing short descriptions about the file/folder path. Lists that have file path descriptors
    will contain one or more elements used to verify that the file exists in the path inputted by the user
    """

    config_dict = {"levels": ["Path to folder containing subfolders which are names of your levels"],
                   "ws2": ["ws2lzfrontend.exe path", "ws2lzfrontend.exe"],
                   "ws2ify": ["run.py path in ws2ify", "run.py"],
                   "bgtool": ["bgtool.exe path", "bgtool.exe"],
                   "SMB_LZ_Tool": ["SMB_LZ_Tool.exe path", "SMB_LZ_Tool"],
                   "gmatool": ["gmatool.exe path", "gmatool.exe"],
                   "GXModelViewer": ["GXModelViewer.exe path in GXModelViewer", "GXModelViewer.exe"],
                   "GxModelViewerNoGUI": ["GxModelViewer.exe path in GxModelViewerNoGUI", "GXModelViewer.exe"],
                   "iso": ["<filename>.iso path, root"],
                   "gcr": ["gcr.exe path", "gcr.exe"]
                   }

    return config_dict
