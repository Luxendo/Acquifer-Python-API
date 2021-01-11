"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
Also make sure that the smart imaging test VI is not running simultaneously, it is also esablishing a connection and would thus prevent new ones
"""
from acquifer import IM

im = IM.TCPIP()
print(im) # should print status, version and port

#%% Check XYZ-position
def printPosition():
    print("X-position: ", im.getXaxis())
    print("Y-position: ", im.getYaxis())
    print("Z-position: ", im.getZaxis())

printPosition()

#%% Get objective
print("Objective number: ", im.getObjectiveNo())

#%% Go to XYZ-position
im.goToXY(12.345, 23.456)
im.goToZ(20.1)

# Check after moving
printPosition()

im.closeSocket()