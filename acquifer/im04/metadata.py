"""
Extract IM metadata from filename.

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

class MetadataParser():

	def getXYPosition_mm(imageName):
		"""Extract the XY-axis coordinates (in mm) from the imageName (for IM4). The coordinates corresponds to the center of the image = objective position."""
		# Parse string + do conversion
		X0mm = int(imageName[65:71]) /1000 # >0
		Y0mm = int(imageName[74:80]) /1000
		
		return X0mm, Y0mm

	def getWellSubPosition(imageName):
		"""Extract the index corresponding to the subposition for that well."""
		return int(imageName[9:11])

	def getZPosition_um(imageName):
		"""Extract the Z-axis coordinates (in um)."""
		return float(imageName[83:89])/10
		
	def getPixelSize_um(imageName):
		"""Extract the pixel size (in um) from the imageName (for IM4)."""
		return float(imageName[34:39])*10**-4
		
	def getObjectiveMagnification(imageName):
		"""Get the magnification as integer."""
		pixSize = getPixelSize_um(imageName)
		if pixSize in pixelSizeToMag:
			return pixelSizeToMag[pixSize]
		else:
			raise KeyError("No pixel size matching in the pixelSizeToMag dictionnary")

	def getObjectiveNA(imageName):
		"""Return the Numerical Aperture of the objective."""
		pixSize = getPixelSize_um(imageName)
		if pixelSizeToNA.has_key(pixSize):
			return pixelSizeToNA[pixSize]
		else:
			raise KeyError("No pixel size matching in the pixelSizeToNA dictionnary")
		
	def getWellId(imageName):
		"""Extract well Id (ex:A001) from the imageName (for IM4)."""
		return imageName[1:5]

	def getWellColumn(imageName):
		"""Extract well column (1-12) from the imageName (for IM4)."""
		return int(imageName[2:5])

	def getWellRow(imageName):
		"""Extract well row (1-8) from the imageName (for IM4)."""
		letter = imageName[1:2]
		return string.ascii_uppercase.index(letter)+1 # alphabetical order +1 since starts at 0


	def getWellIndex(imageName):
		"""Return well number corresponding to order of acquisition by the IM (snake pattern)."""
		return int(imageName[106:111]) 

		
	def getZSlice(imageName):
		"""Return image slice number of the associated Z-Stack serie."""
		return int(imageName[27:30])

		
	def getChannelIndex(imageName):
		"""
		Return integer index of the image channel.
		
		1 = DAPI (385)
		3 = FITC (GFP...)
		5 = TRITC (mCherry...)
		"""
		return int(imageName[22:23])

		
	def getLoopIteration(imageName):
		"""Return the integer index corresponding to the image timepoint."""
		return int(imageName[15:18])

	def getTime(imageName):
		"""Return the time at which the image was recorded."""
		return int(imageName[92:102])
		
	def getLightPower(imageName):
		"""Return relative power (%) used for the acquisition with this channel."""
		return int(imageName[43:47])

		
	def getLightExposure(imageName):
		"""Return exposure time in ms used for the acquisition with this channel."""
		return int(imageName[51:55])

	def getTemperature(imageName):
		"""Return temperature in celsius degrees as measured by the probe at time of acquisition."""
		return float(imageName[59:62])/10


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
