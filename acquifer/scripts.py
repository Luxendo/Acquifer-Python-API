# -*- coding: utf-8 -*-
"""
This module holds function to handle IM scripts, for instance to replace objective-coordinates for prescreen/rescreen.

@author: Laurent Thomas - Acquifer / Luxendo GmbH
"""
import os, clr, sys
from typing import List

dllDir = os.path.join(os.path.dirname(__file__), 'dlls')
#print(dllDir)

sys.path.append(dllDir)
clr.AddReference("ScriptUtils")
from ScriptUtils import ScriptModifier, WellInfo

def replacePositionsInScriptFile(path:str, listPositions:List[WellInfo]):
	"""
	Replace positions in an imsf script.
	Return the path to the centered script
	"""
	return ScriptModifier.ReplacePositionsInScriptFile(path, listPositions)

if __name__ == "__main__":
	path = r"C:\Users\admin\AppData\Local\Temp\test_im_script.imsf" # as written by the PlateViewer tests for instance
	
	listPositions = [WellInfo("a001", 1,2,3,4),
					 WellInfo("B002", 5,6,7,8)]
	
	newScript = replacePositionsInScriptFile(path, listPositions)
	scriptFile = open(newScript, "r")
	lines = scriptFile.read()
	scriptFile.close()
	print(lines)