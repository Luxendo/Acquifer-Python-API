"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
"""
from acquifer import tcpip

#%% Open tcpip communication and switch to script mode
im = tcpip.IM()


#%% Acquire an image
print("Set Metadata and start acquisition.")

im.setSubposition(3)
#im.setBrightField(6, 2, 50, 100)
im.setFluoChannel(1, "010000", 3, 40, 120)

im._setImageFilenameAttribute("CO", 1) # overwrite channel number define when imaging
im.setSubposition(10)
im.setWellNumber(3)
im.setWellId("B001")
im.setTimepoint(2)

im.acquire(1, "BF", 4, 50, 100, 200, 10, 5, False, r"C:\Users\Administrator\Desktop\Laurent")


#%% Close socket at the end
print("\nClose connection port, go back to live mode.")
im.closeSocket()