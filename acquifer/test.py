import os, clr, sys
from typing import List

dllDir = os.path.join(os.path.dirname(__file__), 'dlls')
#print(dllDir)

sys.path.append(dllDir)
clr.AddReference("ScriptUtils")
clr.AddReference("PlateViewer.Common.BaseFunctionality")

from PlateViewer.Common.BaseFunctionality.Classes.DataModels import ImagePlane
help(ImagePlane)
print("Done")