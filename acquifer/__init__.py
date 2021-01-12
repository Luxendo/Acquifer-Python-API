"""
ACQUIFER PYTHON PACKAGE.

Usage 
import acquifer
or 
from acquifer import IM, IM03, IM04

IM is the mother class for IM03 and IM04, it contains default implementations for functions that works both with IM03 and IM04
IM03 and IM04 classes inherit the IM class, therefore only what differs between IM03 and IM04 needs rewriting in the IM03 and IM04 classes

The IM (and descendant) classes are nested with inner classes such as Metadata and TCPIP to allow
IM.Metadata.getWellName()
or
im = IM.TCPIP() # create a new IM object for control over TCP/IP with default IP adress and port

To reduce the length of this single file, the method bodies are separated in private submodules (prefixed with _ : _IM, _IM3, _IM4)
which are imported at the top of this script
"""
from __future__ import division
from . import _IM, _IM03, _IM04
import socket, string


class IM(object):
	"""Mother class of all IMs: implement default behaviour."""
	
	class metadata(object):
		"""contains static method to extract metadata from the filenames."""
		
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
	
	
	class TCPIP(object):
		"""Nested class containing the commands to interact with the IM via the TCPIP port."""
		
		def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=6261):
			"""Initialise a TCP/IP socket for the exchange of commands."""
			# local IP and port (constant)
			self._TCP_IP_   = TCP_IP
			self._TCP_PORT_ = TCP_PORT
			
			# Open a TCP/IP socket to communicate
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._socket.connect((TCP_IP, TCP_PORT))
		
		def __str__(self):
			"""Return a string representation of the object."""
			return "IM v{} at IP:{}, Port:{}, status:{}".format( self.getVersion(), self._TCP_IP_, self._TCP_PORT_, self.getStatus() )
		
		def __getFeedback__(self, size=4):
			"""Generic function to get feedback from the machine after sending a request."""
			return _IM.tcpip.getFeedback(self, size)
		
		def getVersion(self):
			"""Get IM version."""
			return _IM.tcpip.getVersion(self)
		
		def getStatus(self):
			"""Get IM status."""
			return _IM.tcpip.getStatus(self)
		
		def getXaxis(self):
			"""Return the X position of the objective in mm."""
			return _IM.tcpip.getXaxis(self)
		
		def getYaxis(self):
			"""Return the Y position of the objective in mm."""
			return _IM.tcpip.getYaxis(self)
		
		def getZaxis(self):
			"""Return the Z position of the objective in um."""
			return _IM.tcpip.getZaxis(self)
		
		def getLidAxis(self):
			"""Return the position of the lid."""
			_IM.tcpip.getLidAxis(self)
			
		def getObjectiveNo(self):
			"""Return the objective number."""
			return _IM.tcpip.getObjectiveNo(self)
		
		def getLightNo(self):
			"""Return the current channel number. Between 0:None to 6:BF."""
			return _IM.tcpip.getLightNo(self)
		
		def getWellCoordinates(self):
			"""Return the well identifier ex:A001 when the acquisition is running exclusively."""
			return _IM.tcpip.getWellCoordinates(self)
		
		def getZstackCenter(self):
			"""Return the Z-stack center when an acquisition is running exclusively."""
			return _IM.tcpip.getZstackCenter(self)
		
		def getImageFile(self):
			"""Return current image file."""
			return _IM.tcpip.getImageFile(self)
		
		def openLid(self):
			"""Open IM lid."""
			_IM.tcpip.openLid(self)
		
		def closeLid(self):
			"""Close IM lid."""
			_IM.tcpip.closeLid(self)
		
		def goToXY(self,X,Y):
			"""Move objective to position X,Y in mm (max 3 decimal ex:1.111)."""
			_IM.tcpip.goToXY(self,X,Y)
		
		def goToZ(self,Z):
			"""Move objective to position Z in um (max 1 decimal ex:1.1)."""
			_IM.tcpip.goToZ(self, Z)
			
		def setImageDirectory(self, dirPath):
			"""
			Set the main image directory that wil contain the project directories and plate subdirectories.
			
			Folder architecture
			
			Main directory
				|-Project directory 1
				|---- |-Plate Directory ex: timestamp1 + plateTest
				|-----|------|- image1.tif
				|-----|------|- image2.tif
				|-----|
				|-----|-PlateDirectory ex: timestamp2 + plateTest
				|
				|- Project directory 2
			"""
			_IM.tcpip.setImageDirectory(self, dirPath)
		
		def setProject(self, projectName):
			"""
			Set the project name (string) corresponding to a directory name that will contain a new unique plate directory for every new acquisition
			The project name can be e.g. a user name, or the name of an assay that will be repeated for mulitple acquisitions (the plates).
			
			Folder architecture
			
			Main directory
				|-Project directory 1
				|---- |-Plate Directory ex: timestamp1 + plateTest
				|-----|------|- image1.tif
				|-----|------|- image2.tif
				|-----|
				|-----|-PlateDirectory ex: timestamp2 + plateTest
				|
				|- Project directory 2
			"""
			_IM.tcpip.setProject(self, projectName)
		
		def setPlate(self, plateName):
			"""
			Set the plate name (string), used to name the subdirectory where the images will be saved within the Project directory.
			A unique subdirectory name will be formed for every new acquisition, by adding unique timestamp before the plate name provided here.
			
			Folder architecture
			
			Main directory
				|-Project directory 1
				|---- |-Plate Directory ex: timestamp1 + plateTest
				|-----|------|- image1.tif
				|-----|------|- image2.tif
				|-----|
				|-----|-PlateDirectory ex: timestamp2 + plateTest
				|
				|- Project directory 2
			"""
			_IM.tcpip.setPlate(self, plateName)
		
		def openExperimentFile(self, expFilePath):
			"""
			Load parameters from a pre-configred experiment, stored in an .exp file.
			"""
			_IM.tcpip.openExperimentFile(self, expFilePath)
		
		def setScriptFile(self, scriptPath):
			"""Load a pre-configured .imsf script file."""
			_IM.tcpip.setScriptFile(self, scriptPath)
		
		def startScript(self):
			"""Start a previously defined script (using setScript)."""
			_IM.tcpip.startScript(self)
		
		def stopScript(self):
			"""Stop currently executing script."""
			_IM.tcpip.stopScript(self)
		
		def closeSocket(self):
			"""Close TCP/IP port."""
			_IM.tcpip.closeSocket(self)


class IM03(IM):
	"""Implement functionality specific to IM03 model."""
	
	class metadata(IM.metadata):
		"""
		Extract metadata from IM03 filenames.
		
		Example filename:
		"WE00003---A003--PO01--LO001--CO6--SL010--PX16250--PW0040--IN0020--TM246--X032281--Y010963--Z211825--T1375404533.tif"
		"""
		
		@staticmethod
		def getXYPosition_mm(imageName):
			"""Extract the XY-axis coordinates (in mm) from the imageName (for IM4). The coordinates corresponds to the center of the image = objective position."""
			# Parse string + do conversion
			X0mm = int(imageName[74:80]) /1000 # >0
			Y0mm = int(imageName[83:89]) /1000
			
			return X0mm, Y0mm
		
		@staticmethod
		def getWellSubPosition(imageName):
			"""Extract the index corresponding to the subposition for that well."""
			return int(imageName[18:20])
		
		@staticmethod
		def getZPosition_um(imageName):
			"""Extract the Z-axis coordinates (in um)."""
			return float(imageName[92:98])/10
		
		@staticmethod
		def getPixelSize_um(imageName):
			"""Extract the pixel size (in um) from the imageName (for IM4)."""
			return float(imageName[43:48])*10**-4
		
		@staticmethod
		def getObjectiveMagnification(imageName):
			"""Get the magnification as integer."""
			pixSize = IM03.getPixelSize_um(imageName)
			if pixSize in IM03.metadata.pixelSizeToMag: # pixelSizeToMag inherited from IM
				return IM03.metadata.pixelSizeToMag[pixSize]
			else:
				raise KeyError("No pixel size matching in the pixelSizeToMag dictionnary")
		
		@staticmethod
		def getObjectiveNA(imageName):
			"""Return the Numerical Aperture of the objective."""
			pixSize = IM03.metadata.getPixelSize_um(imageName)
			if pixSize in IM03.metadata.pixelSizeToNA:
				return IM03.metadata.pixelSizeToNA[pixSize]
			else:
				raise KeyError("No pixel size matching in the pixelSizeToNA dictionnary")
		
		@staticmethod
		def getWellId(imageName):
			"""Extract well Id (ex:A001) from the imageName."""
			return imageName[10:14]
		
		@staticmethod
		def getWellColumn(imageName):
			"""Extract well column (1-12) from the imageName."""
			return int(imageName[11:14])
		
		@staticmethod
		def getWellRow(imageName):
			"""Extract well row (1-8) from the imageName (for IM4)."""
			letter = imageName[10:11]
			return string.ascii_uppercase.index(letter)+1 # alphabetical order +1 since starts at 0
		
		@staticmethod
		def getWellIndex(imageName):
			"""Return well number corresponding to order of acquisition by the IM (snake pattern)."""
			return int(imageName[2:7]) 
		
		@staticmethod
		def getZSlice(imageName):
			"""Return image slice number of the associated Z-Stack serie."""
			return int(imageName[36:39])
		
		@staticmethod
		def getChannelIndex(imageName):
			"""
			Return integer index of the image channel.
			
			1 = DAPI (385)
			3 = FITC (GFP...)
			5 = TRITC (mCherry...)
			"""
			return int(imageName[31:32])
		
		@staticmethod
		def getLoopIteration(imageName):
			"""Return the integer index corresponding to the image timepoint."""
			return int(imageName[24:27])
		
		@staticmethod
		def getTime(imageName):
			"""Return the time at which the image was recorded."""
			return int(imageName[-14:-4])
		
		@staticmethod
		def getLightPower(imageName):
			"""Return relative power (%) used for the acquisition with this channel."""
			return int(imageName[52:56])

		@staticmethod
		def getLightExposure(imageName):
			"""Return exposure time in ms used for the acquisition with this channel."""
			return int(imageName[60:64])
		
		@staticmethod
		def getTemperature(imageName):
			"""Return temperature in celsius degrees as measured by the probe at time of acquisition."""
			return float(imageName[68:71])/10
	
	class TCPIP(IM.TCPIP):
		"""Implemented remote control via TCPIP for IM03."""
		
		pass
		
		
		
class IM04(IM):
	"""Implement functionality for the IM04."""
	
	class metadata(IM.metadata):
		"""
		Define static method functions to extract metadata from IM04 filenames.
		
		Example filename:
		"-A001--PO01--LO001--CO6--SL001--PX32500--PW0080--IN0020--TM244--X014580--Y011262--Z209501--T1374031802--WE00001.tif"
		"""
		
		@staticmethod
		def getXYPosition_mm(imageName):
			"""Extract the XY-axis coordinates (in mm) from the imageName (for IM4). The coordinates corresponds to the center of the image = objective position."""
			# Parse string + do conversion
			X0mm = int(imageName[65:71]) /1000 # >0
			Y0mm = int(imageName[74:80]) /1000			
			return X0mm, Y0mm

		@staticmethod
		def getWellSubPosition(imageName):
			"""Extract the index corresponding to the subposition for that well."""
			return int(imageName[9:11])

		@staticmethod
		def getZPosition_um(imageName):
			"""Extract the Z-axis coordinates (in um)."""
			return float(imageName[83:89])/10

		@staticmethod
		def getPixelSize_um(imageName):
			"""Extract the pixel size (in um) from the imageName (for IM4)."""
			return float(imageName[34:39])*10**-4

		@staticmethod
		def getObjectiveMagnification(imageName):
			"""Get the magnification as integer."""
			pixSize = IM04.metadata.getPixelSize_um(imageName)
			if pixSize in IM04.metadata.pixelSizeToMag:
				return IM04.metadata.pixelSizeToMag[pixSize]
			else:
				raise KeyError("No pixel size matching in the pixelSizeToMag dictionnary")

		@staticmethod
		def getObjectiveNA(imageName):
			"""Return the Numerical Aperture of the objective."""
			pixSize = IM04.metadata.getPixelSize_um(imageName)
			if pixSize in IM04.metadata.pixelSizeToNA:
				return IM04.metadata.pixelSizeToNA[pixSize]
			else:
				raise KeyError("No pixel size matching in the pixelSizeToNA dictionnary")

		@staticmethod
		def getWellId(imageName):
			"""Extract well Id (ex:A001) from the imageName (for IM4)."""
			return imageName[1:5]
		
		@staticmethod
		def getWellColumn(imageName):
			"""Extract well column (1-12) from the imageName (for IM4)."""
			return int(imageName[2:5])

		@staticmethod
		def getWellRow(imageName):
			"""Extract well row (1-8) from the imageName (for IM4)."""
			letter = imageName[1:2]
			return string.ascii_uppercase.index(letter)+1 # alphabetical order +1 since starts at 0

		@staticmethod
		def getWellIndex(imageName):
			"""Return well number corresponding to order of acquisition by the IM (snake pattern)."""
			return int(imageName[106:111]) 

		@staticmethod
		def getZSlice(imageName):
			"""Return image slice number of the associated Z-Stack serie."""
			return int(imageName[27:30])

		@staticmethod
		def getChannelIndex(imageName):
			"""
			Return integer index of the image channel.
			
			1 = DAPI (385)
			3 = FITC (GFP...)
			5 = TRITC (mCherry...)
			"""
			return int(imageName[22:23])

		@staticmethod
		def getLoopIteration(imageName):
			"""Return the integer index corresponding to the image timepoint."""
			return int(imageName[15:18])

		@staticmethod
		def getTime(imageName):
			"""Return the time at which the image was recorded."""
			return int(imageName[92:102])

		@staticmethod
		def getLightPower(imageName):
			"""Return relative power (%) used for the acquisition with this channel."""
			return int(imageName[43:47])

		@staticmethod
		def getLightExposure(imageName):
			"""Return exposure time in ms used for the acquisition with this channel."""
			return int(imageName[51:55])

		@staticmethod
		def getTemperature(imageName):
			"""Return temperature in celsius degrees as measured by the probe at time of acquisition."""
			return float(imageName[59:62])/10
		
	
	class TCPIP(IM.TCPIP):
		"""Implement remote control of the IM04 via TCPIP interface."""
		
		# Will do some import there
		pass
		