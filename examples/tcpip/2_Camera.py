"""
This script demonstrate the set of commands available to configure the camera field of view and binning settings.

REQUIREMENTS : 
	installing the acquifer python package
	an IM powered-on connected to the pc running the python script
	the option "Block remote connection" of the IM disabled in service settings
	the control software of the IM opened
"""

#%% Import and open tcpip communication
from acquifer import tcpip
import time
im = tcpip.TcpIp()

#%% Set field of view
x = 1000
y = 1000
width = 1024
height = 1024

im.setCamera(x, y, width, height)
time.sleep(5) # wait 5 secs to see the result

#%% Set binning
im.setCameraBinning(2)
time.sleep(5)

#%% Set both camera field of view and binning at once
im.setCamera(0, 0, 1024, 1024, 2) # ends up to a 512x512 image encompassing the top left quadrant of the field of view

#%% Reset to default full field of view (2048 x 2048) and no binning
im.resetCamera()

