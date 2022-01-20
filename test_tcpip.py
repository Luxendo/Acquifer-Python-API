"""
Test the TCPIP port of the IM
Make sure to set the active directory to the root of the repo using cd in the command prompt
"""
from acquifer import tcpip

#%% Open tcpip communication and switch to script mode
im = tcpip.IM()


#%% Acquire a brightfield image
print("Set Metadata and start acquisition.")

im.setSubposition(3)
im.setWellNumber(10)
im.setWellId("B012")
im.setTimepoint(2)
im.acquire(1, "BF", 4, 50, 100, 200, 10, 5, False, r"C:\Users\Administrator\Desktop\Laurent")


#%% Close socket at the end
print("\nClose connection port, go back to live mode.")
im.closeSocket()