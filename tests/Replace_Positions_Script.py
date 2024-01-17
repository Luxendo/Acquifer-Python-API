"""
This script will replace the objective positions in an existing IM script with custom user-provided positions.  
Similar to what the PlateViewer is doing with pre/screen.
This script is motsly for testing, the version that is replacing with pixel positions in images is more interesting for image-analysis.

Running the script in python will prompt for an imsf script, will replace position in it, run it and return the directory where the images were saved.

REQUIREMENTS : 
	installing the acquifer python package
	an IM powered-on connected to the pc running the python script
	the option "Block remote connection" of the IM disabled in service settings
	the control software of the IM opened
"""

#%% Import and open tcpip communication
from acquifer import tcpip

#%% Replace positions in script
from ScriptUtils import ScriptModifier, WellInfo

path_script = input("Paste path to a .imsf script :\n")
path_script = path_script.strip('"') # Remove leading/trailing " from copy/pasting

list_WellPositions = [WellInfo("a001", x = 14.835, y = 10.309, z = 19200.1, wellNumber = 1), 
                      WellInfo("a002", x = 23.839, y = 10.309, z = 19200.1, wellNumber = 2), 
                      WellInfo("a003", x = 32.843, y = 10.309, z = 19200.1, wellNumber = 3), 
                      WellInfo("a004", x = 41.847, y = 10.309, z = 19200.1, wellNumber = 4), 
                      WellInfo("a005", x = 50.851, y = 10.309, z = 19200.1, wellNumber = 5), 
                      WellInfo("a006", x = 59.855, y = 10.309, z = 19200.1, wellNumber = 6), 
                      WellInfo("a007", x = 68.859, y = 10.309, z = 19200.1, wellNumber = 7)]

path_updatedScript = ScriptModifier.ReplacePositionsInScriptFile(path_script, list_WellPositions)


#%% Run script with new positions
im = tcpip.TcpIp()

image_dir = im.runScript(path_updatedScript)

print(f"\nImages saved in {image_dir}")