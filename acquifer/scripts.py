# -*- coding: utf-8 -*-
"""
This module holds function to handle IM scripts, for instance to replace objective-coordinates for prescreen/rescreen.

@author: Laurent Thomas - Acquifer / Luxendo GmbH
"""
import os, clr, sys

dllDir = os.path.join(os.path.dirname(__file__), 'dlls')
#print(dllDir)

sys.path.append(dllDir)
clr.AddReference("ScriptUtils")
from ScriptUtils import ScriptModifier, WellInfo