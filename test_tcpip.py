"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
"""
from acquifer import IM

im = IM.TCPIP()
print(im) # should print status, version and port

# Check XYZ-position
def printPosition():
    print("X-position: ", im.getXaxis())
    print("Y-position: ", im.getYaxis())
    print("Z-position: ", im.getZaxis())

printPosition()

# Go to XYZ-position
im.goToXY(12.345, 23.456)
im.goToZ(20.123)

# Check after moving
printPosition()

im.closeSocket()