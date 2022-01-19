"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
"""
from acquifer import tcpip

#%% Open tcpip communication and switch to script mode
im = tcpip.IM()
im.setMode("script")
print("Connected and activated script mode.")

#%% Acquire a brightfield image
print("Set Metadata and start acquisition.")
im.setBrightField(6, 2, 50, 100)
im._setImageFilenameAttribute("CO", 1) # overwrite channel number define when imaging
im.setSubposition(10)
im.setWellNumber(10)
im.setWellId("B012")
im.setTimepoint(2)
im.acquire(200, 5, 10, r"C:\Users\Administrator\Desktop\Laurent")


#%% Close socket at the end
print("\nClose connection port, go back to live mode.")
im.closeSocket()