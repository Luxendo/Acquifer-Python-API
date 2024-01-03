# -*- coding: utf-8 -*-
"""
This module holds function to handle IM scripts, for instance to replace objective-coordinates for prescreen/rescreen.

@author: Laurent Thomas - Acquifer / Luxendo GmbH
"""

#from importlib_resources import files
import os, clr, sys

dllDir = os.path.join(os.path.dirname(__file__), 'dlls')
print(dllDir)

sys.path.append(dllDir)

clr.AddReference("ScriptUtils")


#data_text = files('acquifer.dlls').joinpath('System.Memory.xml').read_text()

#print(data_text)