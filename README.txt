Created by Pintobean120

Source: https://github.com/PB120/SMBModRocketv1.0

Tutorial: https://www.youtube.com/watch?v=_9hoD28McoQ

Requirements:
- Windows
- Python 3.6 or higher
- Python packages: subprocess, sys, os, glob, shutil, xml.etree.ElementTree
- smblevelworkshop2-withdeps (must have ws2lzfrontend.exe)
- SMB_LZ_Tool
- GXModelViewer
- GXModelViewerNoGUI
- GCR


Functionality

SMBModRocket is an automation tool designed to expedite the process of using
several existing tools from other developers to create stage files.

- .lz.raw creation
- .lz.raw compression
- .gma/.tpl creation
- renaming stage filenames
- moving stage files to //stage folder of ISO
- open GameCube Rebuilder


How to SMBModRocket

1. Create config - stage_helper.py or config_writer.py
Run either stage_helper.py or config_writer.py in Command Line or a Python IDE
to set up your config file. This file will contain paths to your custom stage
models, ws2lzfrontend.exe, SMB_LZ_Tool.exe, etc. Follow the instructions
prompted by the Python file.

Command Line input: python <enter Python file path here>

NOTE: Your custom stages location has to have a very specific structure!
You should have a parent folder that contains child folders - each
child folder's name should be the name of a level.

Ex:
//Levels (parent)
  //Levels//Wavy (child)
  //Levels//Elastic_Platforms
  //Levels//Confidence

The path you enter in the Python program should be the path to the parent folder.

2. Stagefile Modding - stage_helper.py
Enter command, follow instructions prompted by the program.

In order to copy your stage files to the //stage folder of your ISO root, you MUST
have all three stage files in your child folder!!!!

3. Overwrite config
If you need to update your config file or if you screwed it up, run config.py to
overwrite it.


Happy automating :)

Pintobean
