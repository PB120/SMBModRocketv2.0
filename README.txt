Created by Pintobean120

Source: https://github.com/PB120/SMBModRocketv2.0

Tutorial: https://www.youtube.com/watch?v=_9hoD28McoQ

Requirements:
- Windows
- Python 3.6 or higher
- Python packages: subprocess, sys, os, glob, shutil, xml.etree.ElementTree, re, time
- smblevelworkshop2-withdeps (must have ws2lzfrontend.exe)
- bgtool
- SMB_LZ_Tool
- gmatool
- GXModelViewer
- GXModelViewerNoGUI
- GCR


Functionality

SMBModRocket is an automation tool designed to expedite the process of using
several existing tools from other developers to create stage files.

- .lz.raw creation
- vanilla bg data insertion
- .lz creation
- ws2ify usage
- .gma/.tpl creation
- gmatool file merge
- renaming stage filenames
- moving stage files to //stage folder of ISO
- rebuild ISO


How to SMBModRocket

1. Create config - stage_helper.py or config_writer.py
Run either stage_helper.py or config_writer.py in Command Line or a Python IDE
to set up your config file. This file will contain paths to your custom stage
models, ws2lzfrontend.exe, SMB_LZ_Tool.exe, etc. Follow the instructions
prompted by the Python file.

NOTE: Your custom stages location has to have a very specific structure!
You should have a parent folder that contains child folders - each
child folder's name should be the name of a level.

Example diagram:
//Levels (parent)
  //Wavy (child)
  //Elastic_Platforms (child)
  //Confidence (child)

The path you enter in config_writer.py should be the path to the parent folder.


2. Stagefile Modding - stage_helper.py
Follow instructions prompted by the program.


3. Overwrite config
If you need to update your config file or if you screwed it up, run config.py to
overwrite it.


Happy modding :)

Pintobean
