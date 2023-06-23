"""
Extract metadata from image-filename for images acquired with the IM04.

This class contains a set of function to extract metadata by parsing the image file names string of images acquired on an IM04
example filename : "-A001--PO01--LO001--CO6--SL001--PX32500--PW0080--IN0020--TM244--X014580--Y011262--Z209501--T1374031802--WE00001.tif"
"""
from __future__ import division
import string

magToNA = {2:0.06, 
		   4:0.13, 
		   10:0.3,
		   20:0.45,
		   40:0.6}

def getPositionXY_mm(filename):
	"""Extract the XY-axis coordinates (in mm) from the image filename. The coordinates corresponds to the objective XY coordinate and the center of the image if using the full field of view of the camera."""
	# Parse string + do conversion
	x0mm = int(filename[65:71]) /1000 # >0
	y0mm = int(filename[74:80]) /1000
	
	return x0mm, y0mm

def getWellSubPosition(filename):
	"""Extract the index corresponding to the subposition for that well."""
	return int(filename[9:11])

def getPositionZ_um(filename):
	"""Extract the Z-axis coordinates (in um)."""
	return float(filename[83:89])/10
	
def getPixelSize_um(filename):
	"""Extract the pixel size (in um) from the filename."""
	return float(filename[34:39])*10**-4
	
def getWellId(filename):
	"""Extract well Id (ex:A001) from the filename (for IM4)."""
	return filename[1:5]

def getWellColumn(filename):
	"""Extract well column (1-12) from the filename (for IM4)."""
	return int(filename[2:5])

def getWellRow(filename):
	"""Extract well row (1-8) from the filename (for IM4)."""
	letter = filename[1:2]
	return string.ascii_uppercase.index(letter)+1 # alphabetical order +1 since starts at 0

def getWellIndex(filename):
	"""Return well number corresponding to order of acquisition by the IM (snake pattern)."""
	return int(filename[106:111]) 
	
def getZSlice(filename):
	"""Return image slice number of the associated Z-Stack serie."""
	return int(filename[27:30])

def getChannelIndex(filename):
    """
    Return integer index of the image channel.
    
    1 = DAPI (385)
    3 = FITC (GFP...)
    5 = TRITC (mCherry...)
    """
    return int(filename[22:23])

def getTimepoint(filename):
	"""Return the integer index corresponding to the image timepoint."""
	return int(filename[15:18])

def getTime(filename):
    """Return the time at which the image was recorded."""
    return int(filename[92:102])
    
def getLightPower(filename):
	"""Return relative power (%) used for the acquisition with this channel."""
	return int(filename[43:47])
	
def getExposure(filename):
	"""Return exposure time in ms used for the acquisition with this channel."""
	return int(filename[51:55])

def getTemperature(filename):
	"""Return temperature in celsius degrees as measured by the probe at time of acquisition."""
	return float(filename[59:62])/10

def convertXY_PixToIM(Xpix, Ypix, PixelSize_um, X0mm, Y0mm, Image_Width=2048, Image_Height=2048):
	"""
	Convert XY pixel coordinates of some item in an image acquired with the Acquifer IM, to the corresponding XY IM coordinates.
	
	Parameters
	----------
	Xpix, Ypix : int 
		pixel coordinates of the item (its center) in the image
	PixelSize  : float
		size of one pixel in mm for the image
	X0mm, Y0mm : float
		the IM axis coordinates in mm for the center of the image
	Image_Width, Image_Height : int
		dimension of the image (default to 2048x2048 if no binning)
	
	Returns
	-------
	Xout, Yout: float
		X,Y Coordinates of the item in IM standards
	"""
	# Do the conversion
	Xout = X0mm + (-Image_Width/2  + Xpix)*PixelSize_um*10**-3        	     # result in mm
	Yout = Y0mm + (-Image_Height/2 + Image_Height -Ypix)*PixelSize_um*10**-3 # Consider for Y the 0 pixel coordinates at the image bottom (ie Y axis oriented towards the top). From the image center, substract half the image towards the bottom (-Image_Height/2, we are now at the image bottom), then add the Image height (+ Image_Height, we are at the image top) then substract the Y center to go down to the y item coordinates
	
	# Allow only 3 decimal (in jobs file)
	Xout = round(Xout,3) 
	Yout = round(Yout,3)
	
	return Xout, Yout