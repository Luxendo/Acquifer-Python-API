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
import MTM, cv2, os

hasUpdatedValues = input("Did you update values for path_prescreen, path_rescreen, path_template and zref ? (y/n)")

if not hasUpdatedValues.strip().lower() in ["y", "yes"]:
	raise InterruptedError("Update values first")

#%% Input scripts
path_prescreen = ""
path_rescreen  = ""
path_template = r"C:\Users\Laurent.Thomas\Documents\Dataset\temp.tif"

zref = 0.0

#%% Run prescript
im = tcpip.TcpIp()
directory_prescreen = im.runScript(path_prescreen)


#%% Run template matching
template = cv2.imread(path_template, -1)
directory_detected = os.path.join(directory_prescreen, "detected")
if not os.path.exists(directory_detected):
	os.mkdir(directory_detected)

listPositions = []
for filename in os.listdir(directory_prescreen):
	
	if not filename.endswith(".tif"):
		continue
	
	if not "CO1" in filename:
		continue
	
	filepath = os.path.join(directory_prescreen, filename)
	
	image = cv2.imread(filepath, -1)
	
	list_Hits = MTM.matchTemplates(listTemplates=[("template", template)], 
								   image = image,
								   N_object = 1, 
								   score_threshold=0.5, 
								   method=cv2.TM_CCOEFF_NORMED, 
								   maxOverlap=0)
	
	bbox = list_Hits["BBox"][0]
	x,y,width, height = bbox
	bboxCenter_x = int(x + width/2)
	bboxCenter_y = int(y + height/2)
	
	# Crop detected region and save it
	foundImage = image[x:width, y:height]
	cv2.imwrite(os.path.join(directory_detected, filename), foundImage)
	
	# Create a pixel poxition and add it to the list
	position = PixelPosition(bboxCenter_x, bboxCenter_y, float(zref), filepath)
	listPositions.append(position)

#%% Replace with PixelPosition
script = scripts.ReplacePositionsInScriptFile(path_rescreen, listPositions)

#%% Run script with new positions
im = tcpip.TcpIp()
im.runScript(script)