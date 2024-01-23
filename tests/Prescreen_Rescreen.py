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

#%% Checks
hasUpdatedValues = input("Did you update values for path_prescreen, path_rescreen, path_template and zref ? (y/n)")

if not hasUpdatedValues.strip().lower() in ["y", "yes"]:
	raise InterruptedError("Update values first")

#%% Input scripts
path_prescreen = r"C:\Users\Administrator\Downloads\2X-script.imsf"
path_rescreen  = r"C:\Users\Administrator\Downloads\4X-script.imsf"
path_template = r"C:\Users\Administrator\Downloads\medaka_crop.tif"

zref = 21500.1

#%% Run prescript
scope = tcpip.TcpIp()
directory_prescreen = scope.runScript(path_prescreen)


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
	
	hits = MTM.matchTemplates(listTemplates=[("template", template)], 
								   image = image,
								   N_object = 1, 
								   score_threshold=0.5, 
								   method=cv2.TM_CCOEFF_NORMED, 
								   maxOverlap=0)
	
	if len(hits) == 0:
		continue
	
	print(hits)
	
	score = hits["Score"][0]
	if score < 0.5:
		continue
	
	bbox = hits["BBox"][0]
	x,y,width, height = bbox
	bboxCenter_x = int(x + width/2)
	bboxCenter_y = int(y + height/2)
	
	# Crop detected region and save it
	foundImage = image[x : x+width, y : y+height]
	cv2.imwrite(os.path.join(directory_detected, filename), foundImage)
	
	# Create a pixel poxition and add it to the list
	position = PixelPosition(bboxCenter_x, bboxCenter_y, float(zref), filepath)
	listPositions.append(position)

#%% Update positions and run script with new positions
script = scripts.replacePositionsInScriptFile(path_rescreen, listPositions)

scope = tcpip.TcpIp()
scope.runScript(script)