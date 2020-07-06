import config_writer as cw
import configparser
import subprocess
import sys
import os
import shutil
import xml.etree.ElementTree as et
import config_writer
import re
import time

config = configparser.ConfigParser()
parser = configparser.ConfigParser()

cw.exec_main_block()
parser.read("config.ini")


paths = cw.Paths(parser.get("Paths/directories", "your levels"),
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
