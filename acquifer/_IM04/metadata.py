"""
Extract IM04 metadata from filename.

Python 2 (incl.Fiji) or 3
This class contains a set of function to extract metadata by parsing the image file names string of images acquired on an IM04
example filename : "-A001--PO01--LO001--CO6--SL001--PX32500--PW0080--IN0020--TM244--X014580--Y011262--Z209501--T1374031802--WE00001.tif"
It also contains a function convertXY_PixToIM to convert from pixel coordinates in an image to the corresponding machine coordinates
"""
from __future__ import division
import string

pixelSizeToMag = {3.25:2, 
				  1.625:4, 
				  0.650:10, 
				  0.325:20} # Pixel size (um) to objective magn.

pixelSizeToNA = {3.25:0.06, 
				 1.625:0.13, 
				 0.650:0.3, 
				 0.325:0.45} # Pixel size (um) to objective NA

magToNA = {2:0.06, 
		   4:0.13, 
		   10:0.3,
		   20:0.45,
		   40:0.6}

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
