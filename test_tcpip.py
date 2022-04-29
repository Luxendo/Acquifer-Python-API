"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
"""
#%% Import and open tcpip communication
from acquifer import tcpip

im = tcpip.TcpIp()

#%% Set project folder and plate ID
mode = "script"
#mode = "live"
im.setMode(mode)
im.setDefaultProjectFolder(r"C:\Users\Administrator\Desktop\Laurent\test2")
im.setPlateId("test_{}_mode".format(mode))
#im.setPlateId("?wfw\#:")

objectiveIndex = 2 # 2 = 4X

#%% Run autofocus on Brightfield
im.setCamera(256, 256, 512, 512) # Use ROI for autofocus
zFocus = im.runSoftwareAutoFocus(objectiveIndex, "bf", 2, 50, 100, 200, 10, 10)

#%% Acquire an image
#print("Set Metadata")

im.setMetadataSubposition(3)
#im.setBrightField(6, 2, 50, 100)
#im.setFluoChannel(1, "010000", 3, 40, 120)
#im.setFluoChannel(1, "001000", 3, 80, 120)

#im._setImageFilenameAttribute("CO", 1) # overwrite channel number define when imaging
im.setMetadataWellNumber(3)
im.setMetadataWellId("B001")
im.setMetadataTimepoint(2)

im.resetCamera()
im.acquire(1, objectiveIndex, "001000", 3, 80, 120, zFocus, 10, 5)


#%% Close socket at the end
im.closeConnection()