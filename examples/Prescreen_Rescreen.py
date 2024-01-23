"""
This script provides an automated solution for targeted high-resolution imaging of regions of interest (ROIs) with an ACQUIFER Imaging Machine.  
It provides a similar functionalitiy than the PlateViewer when used to designate regions of interest, except here the ROIs are automatically detected, and the process is fully automated.  

The execution sequence is as following : 
 - low resolution imaging using a template IM script
 - detection of objects in images (here using template matching to detect a single object, the script could be updated to detect multiple objects in each image)
 - updating second IM script for high-resolution imaging, with positions of detected object
 - running of modified high-resolution script
 
TODO Before running the script (the script will anyway ask for confirmation)  
- update the path to the prescreen and rescreen scripts (IM scripts with .imsf extension)  
- update the path to a template image, representing the object to localize, it should be smaller than the acquired images  
- update the Z-position for the rescreen (zref)  

PYTHON - REQUIREMENTS (tested with Python 3.10 but should work with any python 3 version): 
- acquifer (pip install acquifer)
- opencv (pip install opencv-python-headless)
- Multi-Template-Matching, version 1.6.6 (pip install Multi-Template-Matching == 1.6.6) 

Other requirements :
 - the is IM powered-on, and the control software running
 - the option "Block remote connection" of the IM is disabled in service settings
 
NOTE
The spyder IDE was sometimes raising issues (AddRerence function missing) when re-running the script.  
In this case, try using another IDE such as Visual Studio Code.   
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
path_prescreen = r".\2X-script.imsf"
path_rescreen  = r".\4X-script.imsf"
path_template  = r".\medaka_crop.tif"

zref = 21500.1 # Z-plane position (µm) for the rescreen, to read from the GUI for one in-focus sample with the imaging settings of the rescreen scripts 

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