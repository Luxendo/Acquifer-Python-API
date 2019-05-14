'''
This class contains a set of function to extract metadata by parsing the image file names string
It also contains a function convertXY_PixToIM to convert from pixel coordinates in an image to the corresponding machine coordinates
'''
from __future__ import division


def getXY_mm(ImageName):
	'''Extract the axis coordinates (in mm) from the ImageName (for IM4). The coordinates corresponds to the center of the image.'''
	# Parse string + do conversion
	X0mm = int(ImageName[65:71]) /1000 # >0
	Y0mm = int(ImageName[74:80]) /1000
	
	return X0mm, Y0mm

	
def getPixelSize_um(ImageName):
	'''Extract the pixel size (in um) from the ImageName (for IM4)'''
	return float(ImageName[34:39])*10**-4
	

def getWellId(ImageName):
	'''Extract well Id (ex:A001) from the ImageName (for IM4)'''
	return ImageName[1:5]
	

def getWellNum(ImageName):
	'''Return well number corresponding to order of acquisition by the IM (snake pattern)'''
	return int(ImageName[106:111]) 

	
def getSlice(ImageName):
	'''Return image slice number of the associated Z-Stack serie'''
	return int(ImageName[27:30])

	
def getChannelIndex(ImageName):
	'''Return integer index of the image channel'''
	return int(ImageName[22:23])

	
def getIterationIndex(ImageName):
	'''Return the integer index corresponding to the image timepoint'''
	return int(ImageName[15:18])

	
def getPower(ImageName):
	'''Return relative power (%) used for the acquisition with this channel'''
	return int(ImageName[43:47])

	
def getExposure(ImageName):
	'''Return exposure time in ms used for the acquisition with this channel'''
	return int(ImageName[51:55])


def convertXY_PixToIM(Xpix, Ypix, PixelSize_um, X0mm, Y0mm, Image_Width=2048, Image_Height=2048):
	'''
	Convert XY pixel coordinates of some item in an image acquired with the Acquifer IM, to the corresponding XY IM coordinates
	
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
	------
	Xout, Yout: float
		X,Y Coordinates of the item in IM standards
	'''
	# Do the conversion
	Xout = X0mm + (-Image_Width/2  + Xpix)*PixelSize_um*10**-3        	     # result in mm
	Yout = Y0mm + (-Image_Height/2 + Image_Height -Ypix)*PixelSize_um*10**-3 # Consider for Y the 0 pixel coordinates at the image bottom (ie Y axis oriented towards the top). From the image center, substract half the image towards the bottom (-Image_Height/2, we are now at the image bottom), then add the Image height (+ Image_Height, we are at the image top) then substract the Y center to go down to the y item coordinates
	
	# Allow only 3 decimal (in jobs file)
	Xout = round(Xout,3) 
	Yout = round(Yout,3)
	
	return Xout, Yout