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
clr.AddReference("PlateViewer.Common.BaseFunctionality")

from ScriptUtils import ScriptModifier, WellInfo, PixelPosition
from PlateViewer.Common.BaseFunctionality.Classes.DataModels import ImagePlane

def replacePositionsInScriptFile(path:str, listPositions:List[PixelPosition]):
	"""
	Replace positions in an imsf script, with image-positions (ex: object found in images) 
	Return the path to the centered script
	"""
	return ScriptModifier.ReplacePositionsInScriptFile(path, listPositions)

if __name__ == "__main__":
	
	path = r"C:\Users\admin\AppData\Local\Temp\test_im_script.imsf" # as written by the PlateViewer tests for instance
	
	# Replace with WellInfo
	listPositions = [WellInfo("a001", 1,2,3,4),
					 WellInfo("B002", 5,6,7,8)]
	
	script1 = ScriptModifier.ReplacePositionsInScriptFile(path, listPositions)
	
	# Read content of centered scripts and print it
	scriptFile = open(script1, "r")
	lines = scriptFile.read()
	scriptFile.close()
	print(lines)


	# Replace with PixelPosition
	image_filename = r"C:\Users\admin\Documents\TestDataset\-A005--PO01--LO001--CO1--SL002--PX65000--PW0070--IN0020--TM228--X050588--Y010849--Z184986--T0000017069--WE00005.tif"
	image = ImagePlane(image_filename)

	listPositions2 = [PixelPosition(250, 300, image, 1),
				  	  PixelPosition(600, 300, image, 2)]


	script2 = ScriptModifier.ReplacePositionsInScriptFile(path, listPositions2)

	scriptFile = open(script2, "r")
	lines = scriptFile.read()
	scriptFile.close()
	print(lines)