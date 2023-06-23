"""
This script demsonstrate the set of metadata that can be extracted from the image filenames.
"""
from acquifer import metadata

# Example filename
filename = "-A002--PO01--LO002--CO6--SL010--PX32500--PW0080--IN0020--TM281--X023590--Y011262--Z211710--T0200262822--WE00002.tif"

print("Image name :", filename)

print("\nWell Id :", metadata.getWellId(filename)) 

print ("Plate column :", metadata.getWellColumn(filename))
print ("Plate row :",    metadata.getWellRow(filename))

print ("Well subposition :", metadata.getWellSubPosition(filename))

print ("Well index (order of acquisition) :", metadata.getWellIndex(filename))

print ("Positions XY (mm): ", metadata.getPositionXY_mm(filename))
print ("Position Z (micrometers): ",   metadata.getPositionZ_um(filename))

print ("Z-slice Number : ", metadata.getZSlice(filename))

print ("Light power (%) :", metadata.getLightPower(filename))

print ("Exposure time (ms) :", metadata.getExposure(filename))

print ("Channel index :", metadata.getChannelIndex(filename)) 

print ("Pixel Size (um): ", metadata.getPixelSize_um(filename))

print ("Timepoint :", metadata.getTimepoint(filename))

print ("Temperature (Celsius)", metadata.getTemperature(filename))