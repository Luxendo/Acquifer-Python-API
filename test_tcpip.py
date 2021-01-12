"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
Also make sure that the smart imaging test VI is not running simultaneously, it is also esablishing a connection and would thus prevent new ones

Tested with v 4.10.07
"""
from acquifer import IM
import time

im = IM.TCPIP()
print(im) # should print status, version and port

#%% Lid
print("Lid position: ", im.getLidAxis())
#%% Check XYZ-position
def printPositions():
    print("") # new line
    print("X-position: ", im.getXaxis())
    print("Y-position: ", im.getYaxis())
    print("Z-position: ", im.getZaxis())

printPositions()

#%% Get objective
print("\nObjective number: ", im.getObjectiveNo())
print("Channel number: ", im.getLightNo())

#%% Go to XYZ-position
print("\nMove objective along XYZ")
im.goToXY(12.345, 23.456)
im.goToZ(20.1)

# Check after moving
printPositions()

#%% setScript, start, stop
print("Start a known script and stop it after 20s")
scriptPath = r"D:\IMAGING-DATA\SCRIPTS\2x.imsf"
im.setScriptFile(scriptPath)
im.startScript()
time.sleep(20) # wait 20 seconds
im.stopScript()

#%% Experiment file
print("Load preconfigured experiment (imef file), this should update the GUI accordingly")
imef = "D:\IMAGING-DATA\EXPERIMENT\DEFAULT\Default.imef"
im.openExperimentFile(imef)

#%% Close socket at the end
print("\nClose connection port")
im.closeSocket()