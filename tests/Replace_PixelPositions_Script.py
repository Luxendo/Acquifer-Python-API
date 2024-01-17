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
from acquifer import tcpip, scripts
from ScriptUtils import PixelPosition

path_rescreen_script = "C:\Users\Laurent\Downloads\10x-bf.imsf" # this script is only used to get the high-res settings, positios will be replaced with the one defined below

# Replace with PixelPosition
image_filename = "D:\IMAGING-DATA\IMAGES\20240117_152537_default\-A001--PO01--LO001--CO1--SL001--PX32500--PW0040--IN0030--TM202--X014835--Y010309--Z192001--T0000000000--WE00001.tif"

zref = 19449.7 # in um, this will be the Z-position for imaging, or for the starting point of the AF

listPositions = [PixelPosition(424, 1696, zref, image_filename, 1),
                 PixelPosition(240, 1000, zref, image_filename, 2)]


script = scripts.ReplacePositionsInScriptFile(path, listPositions)


#%% Run script with new positions
im = tcpip.TcpIp()
im.runScript(script)