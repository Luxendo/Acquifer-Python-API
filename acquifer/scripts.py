# -*- coding: utf-8 -*-
"""
This module holds function to handle IM scripts, for instance to replace objective-coordinates for prescreen/rescreen.

@author: Laurent Thomas - Acquifer / Luxendo GmbH
"""

#from importlib_resources import files
import os, clr, sys

dllDir = os.path.join(os.path.dirname(__file__), 'dlls')
#print(dllDir)

sys.path.append(dllDir)

clr.AddReference("ScriptUtils")


from ScriptUtils import ScriptModifier, WellInfo

well = WellInfo("a001", 1, 1 , 1, 1)
print(str(well)) # priting the object wont show the string representation, so first need to convert to string

#listWells = WellInfo
#ScriptModifier.ReplacePositions