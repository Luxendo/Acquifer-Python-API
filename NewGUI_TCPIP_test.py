"""
Test script for the TCPIP connection.
Start the IM GUI software, deactivate block exernal connection (restart if that was not deactivated)
Then run this script in Fiji (jython) or in a normal python interpreter
"""

import socket, time, os

def isPositiveInteger(value):
	"""Return false if the input is not a strictly positive >0 integer."""
	
	if not isinstance(value, int) or value < 1 :
		return False
	
	return True

def isNumber(value):
	"""Test if an input is a number ie int or float."""
	return isinstance(value, (int, float))

def checkIntensity(intensity):
	"""Throw a ValueError if the intensity is not an integer in range 0-100."""
	
	if not isinstance(intensity, int):
		raise ValueError("Intensity must be an integer value.")

	if intensity < 0 or intensity > 100 :
		raise ValueError("Intensity must be in range [0-100].")

def checkExposure(exposure):
	"""Throw a ValueError if the exposure is not an positive integer value."""
	if not isinstance(exposure, int) or exposure < 0 :
		raise ValueError("Exposure must be a positive integer value.")


class IM(object):
	"""Object representing the IM from ACQUIFER defined with a list of methods to control it."""

	def __init__(self, port=6200):
		"""Initialize a TCP/IP socket for the exchange of commands."""
		
		self._socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # IPv6 on latest IM 
		try:
			self._socket.connect(("localhost", port))
		
		except socket.error:
			msg = ("Cannot connect to IM GUI.\nMake sure an IM is available, powered-on and the IM program is running.\n" +
			"Also make sure that the option 'Block remote connection' of the admin panel is deactivated, and that the port numbers match (port 6200 is used by default in IM constructor if none specified).")
			raise socket.error(msg)

	def closeSocket(self):
		"""
		Close the socket, making it available to other resources.
		After closing the socket, no commands can be sent anymore via this IM instance. 
		This should be called at the end of external scripts.
		It also switches back to 'live' mode in case the machine is in script mode.
		"""
		self.setMode("live")
		self._socket.close()

	def sendCommand(self, stringCommand):
		"""
		Send a string command to the IM and wait 50ms for processing of the command.
		The command is converted to a bytearray before sending.
		""" 
		self._socket.sendall(bytearray(stringCommand, "ascii"))
		time.sleep(0.05) # wait 50ms, before sending another command (which is usually whats done next, e.g. with _getFeedback

	def _getFeedback(self, size=256):
		"""Read a value back from the IM after a "get" command."""
		return self._socket.recv(size).decode("ascii")

	def _waitForFinished(self):
		"""
		This function calls getFeedback with the correct size corresponding to "finished". 
		It will pause code execution until this amount of bytes can be read.
		"""
		if self._getFeedback(10) == "error": # chose 10 but could be another value
			raise Exception("Could not execute command.")

	def _getValueAsType(self, command, cast):
		"""Send a command, get the feedback and cast it to the type provided by the cast function ex: int."""
		self.sendCommand(command)
		return cast(self._getFeedback())

	def _getIntegerValue(self, command):
		"""Send a command and parse the feedback to an integer value."""
		return self._getValueAsType(command, int)

	def _getFloatValue(self, command):
		"""Send a command and parse the feedback to a float value."""
		return self._getValueAsType(command, float)

	def _getBooleanValue(self, command):
		"""Send a command and parse the feedback to a boolean value (0/1)."""
		return self._getValueAsType(command, int) # dont use bool, bool of a non-empty string is always true, even bool("0")

	def openLid(self):
		self.sendCommand("OpenLid()")

	def closeLid(self):
		self.sendCommand("CloseLid()")

	def isLidClosed(self):
		"""Check if the lid is closed."""
		return self._getBooleanValue("LidClosed()")

	def isLidOpened(self):
		"""Check if lid is opened."""
		return self._getBooleanValue("LidOpened()")

	def getMode(self):
		"""Return current acquisition mode either "live" or "script"."""
		return "live" if self._getBooleanValue("LiveModeActive()") else "script"

	def isScriptRunning(self):
		"""
		Check if a script is running i.e when LiveMode is not active.
		If a script is running, tcpip commands should not be sent (except to ask for the machine state).
		"""
		return not self._getBooleanValue("LiveModeActive()")

	def isLiveModeActive(self):
		"""
		Check if live mode is active, ie no script is running and tcpip commands can be sent.
		"""
		return self._getBooleanValue("LiveModeActive()")

	def isTemperatureRegulated(self):
		return self._getBooleanValue("GetTemperatureRegulation()")
	
	def getTemperatureAmbiant(self):
		"""Return ambiant temperature in celsius degrees."""
		return self._getFloatValue("GetAmbientTemperature(TemperatureUnit.Celsius)")
	
	def getTemperatureSample(self):
		"""Return the sample temperature in celsius degrees."""
		return self._getFloatValue("GetSampleTemperature(TemperatureUnit.Celsius)")

	def getTemperatureTarget(self):
		"""Return the target temperature in celsius degrees."""
		return self._getFloatValue("GetTargetTemperature(TemperatureUnit.Celsius)")

	def setTemperatureRegulation(self, state):
		"""
		Activate (state=True) or deactivate (state=False) temperature regulation.
		"""
		if state :
			self.sendCommand("SetTemperatureRegulation(1)")
		
		else :
			self.sendCommand("SetTemperatureRegulation(0)")

	def setTemperatureTarget(self, temp):
		"""
		Set the target temperature to a given value in degree celsius (with 0.1 precision).
		Note : This does NOT switch on temperature regulation !
		Call setTemperatureRegulation(True) to activate the regulation.
		"""
		if (temp < 18 or temp > 34):
			raise ValueError("Target temperature must be in range [18;34].")
		
		self.sendCommand( "SetTargetTemperature({:.1f}, TemperatureUnit.Celsius)".format(temp) )

	def getNumberOfColumns(self):
		"""Return the number of plate columns."""
		return self._getIntegerValue("GetCountWellsX()")

	def getNumberOfRows(self):
		"""Return the number of plate rows."""
		return self._getIntegerValue("GetCountWellsY()")

	def getObjectiveIndex(self):
		"""Return the currently selected objective-index (1 to 4)."""
		return self._getIntegerValue("GetObjective()")

	def getPositionX(self):
		"""Return the current objective x-axis position in mm."""
		return self._getFloatValue("GetXPosition()")

	def getPositionY(self):
		"""Return the current objective y-axis position in mm."""
		return self._getFloatValue("GetYPosition()")

	def getPositionZ(self):
		"""Return the current objective z-axis position in µm."""
		return self._getFloatValue("GetZPosition()")

	def goToXY(self,x,y):
		"""Move to position x,y in mm, with 0.001 decimal precision."""
		cmd = "GotoXY({:.3f},{:.3f})".format(x,y) # force max 3 decimal positions
		self.sendCommand(cmd)

	def goToZ(self, z):
		"""Move to Z-position in µm with 0.1 precision."""
		cmd = "GotoZ({:.1f})".format(z)
		self.sendCommand(cmd)

	def goToXYZ(self,x,y,z):
		"""Move to x,y position (mm, 0.001 precision) and z-position in µm (0.1 precision)"""
		cmd = "GotoXYZ({:.3f},{:.3f},{:.1f})".format(x,y,z)
		self.sendCommand(cmd)

	def runScript(self, scriptPath):
		"""
		Start a script.
		Start a .imsf or .cs script to run an acquisition.
		This command can be called only if no script is running.
		"""
		
		if not (scriptPath.endswith(".imsf") or scriptPath.endswith(".cs")):
			raise ValueError("Script must be a .imsf or .cs file.")
		
		if not os.path.exists(scriptPath):
			raise ValueError("Script file not existing : {}".format(scriptPath))
			
		cmd = "RunScript({})".format(scriptPath)
		self.sendCommand(cmd)

	def stopScript(self):
		"""Stop any script currently running."""
		self.sendCommand("StopScript()")

	def setCamera(self, binning, x, y, width, height):
		"""
		Set acquisition parameters of the camera (binning and/or acquisition-ROI).
		The provided parameters will be used for the next "acquire" commands (sent via the gui or tcpip).
		Exposure time are defined for each channel using the setBrightfield or setFluo commands.
		"""
		if binning not in (1,2,4):
			raise ValueError("Binning should be 1,2 or 4.")
		
		largerThan2048 = lambda value : value > 2048
		negative	   = lambda value : value < 0 
		
		bbox = map(int, (x,y,width,height)) # Make sure they are integer
		
		if any(map(largerThan2048, bbox)) or any(map(negative, bbox)):
			raise ValueError("x,y,width,height must be in range [0;2048]")
		
		self.sendCommand("SetCamera({},{},{},{},{})".format(binning, *bbox))

	def setObjective(self, index):
		"""Set the objective based on the index (1 to 4)."""
		
		if index not in (1,2,3,4):
			raise ValueError("Objective index must be in range [1,4].") 
		
		self.sendCommand( "SetObjective({})".format(index) )

	def _setImageFilenameAttribute(self, prefix, value):
		
		listPrefix = ("WE", "PO", "LO", "CO", "Coordinate") # Coordinate is the wellID
		if not (prefix in listPrefix ):
			raise ValueError("Prefix must be one of " + listPrefix)
		
		cmd = "SetImageFileNameAttribute(ImageFileNameAttribute.{}, {})".format(prefix, value)
		print(cmd)
		self.sendCommand(cmd)

	def setWellNumber(self, number):
		"""Update well number used to name image files for the next acquisitions (WE tag)."""
		
		if not isinstance(number, int) or number < 1:
			raise ValueError("Well number must be a strictly positive integer.""")
		
		self._setImageFilenameAttribute("WE", number)

	def setWellId(self, wellID):
		"""Update the well ID (ex: "A001"), used to name the image files for the next acquisitions."""
		
		if not isinstance(wellID, str):
			raise ValueError("WellID must be a string ex: 'A001'.")
		
		if not wellID[0].isalpha():
			raise ValueError("WellID must start with a letter, example of well ID 'A001'.")
		
		self._setImageFilenameAttribute("Coordinate", wellID)

	def setSubposition(self, subposition):
		"""Update the well subposition index (within a given well), used to name the image files for the next acquisitions (PO tag)."""
		
		if not isinstance(subposition, int) or subposition < 1:
			raise ValueError("Subposition must be a strictly positive integer.""")
		
		self._setImageFilenameAttribute("PO", subposition)

	def setTimepoint(self, timepoint):
		"""Update the timepoint (or loop iteration) index, used to name the image files for the next acquisitions (LO tag)."""

		if not isinstance(timepoint, int) or timepoint < 1:
			raise ValueError("Timepoint must be a strictly positive integer.""")
		
		self._setImageFilenameAttribute("LO", timepoint) # LO for LOOP

	def setBrightField(self, channelNumber, filterIndex, intensity, exposure, offsetAF, lightConstantOn):
		"""
		Activate the brightfield channel with a given intensity, exposure time and using the detection filter at the given positional index.
		In Live mode, the channel is directly switched on, and must be switched off using the setBrightFieldOff command.
		In script mode, the channel is switched on synchronously with the camera, with the next acquire commands.
		- channelNumber : this value is used for the image file name (tag CO)
		- filterIndex   : positional index of the detection filter (1 to 4), depeneding on the filter, the overall image intensity varies.
		- intensity     : intensity for the brightfield light source
		- exposure      : exposure time in ms, used by the camera when imaging this channel 
		- offsetAF
		- lightConstantOn : if true, the light is constantly on (only during the acquisition in script mode)
							otherwise the light source is synchronised with the camera exposure, and thus is blinking.
		"""
		if not isPositiveInteger(channelNumber):
			raise ValueError("Channel number must be a strictly positive integer.")

		if not filterIndex in (1,2,3,4) : 
			raise ValueError("Filter index must be one of 1,2,3,4.")
		
		if not isNumber(offsetAF):
			raise ValueError("Autofocus offset must be a number, passed : {}.".format(offsetAF))
		
		if not isinstance(lightConstantOn, bool):
			raise ValueError("lightConstantOn must be a boolean value (True/False).")
			
		checkIntensity(intensity)
		checkExposure(exposure)
		
		lightConstantOn = "true" if lightConstantOn else "false" # just making sure to use a lower case for true : python boolean is True
		self.sendCommand("SetBrightField({}, {}, {}, {}, {}, {})".format(channelNumber, filterIndex, intensity, exposure, offsetAF, lightConstantOn) )

	def setBrightFieldOff(self):
		"""
		Switch the brightfield channel off in live mode, by setting intensity and exposure time to 0.
		In script mode this has no utility : on/off switching is synchronized with the camera acquisition.
		"""
		if self.getMode() == "live":
			self.sendCommand("SetBrightField(1, 1, 0, 0, 0, false)") # any channel, filter should do, as long as intensity is 0

	def acquire(self, zStackCenter, nSlices, zStepSize, saveDirectory=""):
		"""
		Acquire a Z-stack composed of nSlices, distributed evenly around a Z-center position, using current objective, channel and camera settings.

		Images are named according to the IM filenaming convention, and saved in saveDirectory, or in the default acquisition directory if none is mentioned.
		Use setWellID, setWellSubposition, setLoopIteration to update image-metadata used for filenaming before calling acquire.
		
		For the stack, the center position is typically the one found by autofocus.
		Each slice is distant from the next by zStepSize.
		For odd number of slices, the center slice is acquired at Z-position zStackCenter and (nSlices-1)/2 are acquired above and below this center slice.
		For even number of slices, nSlices/2 slices are acquired above and below the center position. No images is acquired for the center position.
		
		zStepSize    : distance between slices in µm with 0.1 precision
		zStackCenter : center position of the Z-stack in µm, with 0.1 precision.
		"""
		if saveDirectory:
			cmd = "Acquire({},{:.1f},{:.1f},{})".format(nSlices, zStepSize, zStackCenter, saveDirectory)
		else:
			cmd = "Acquire({},{:.1f},{:.1f})".format(nSlices, zStepSize, zStackCenter)
		
		self.sendCommand(cmd)

	def setMode(self, mode):
		"""
		Set the acquisition mode to either "live" or "script.
		This function first check the current mode before changing it if needed.
		"""
		
		mode = mode.lower()
		
		# Check current mode, this prevent error message from IM when switching to current mode
		if mode == self.getMode():
			return
		
		if mode == "script":
			self.sendCommand("SetScriptMode(1)")
		
		elif mode == "live":
			self.sendCommand("SetScriptMode(0)")
		
		else:
			raise ValueError("Mode can be either 'script' or 'live'.")
		
		self._waitForFinished()
	
	def runSoftwareAutofocus(self, zStackCenter, nSlices, zStepSize):
		"""
		Run a software autofocus with current channel and objective settings.
		Return the Z-position of the focused slice.
		If no channel is currently active the autofocus returns the zStackCenter value.
		The focused planed is chosen as the most focused slice from a stack centred on a given Z-position, with nSlices each separated by zStepSize.
		zStackCenter : centre of the stack, position in µm with 0.1 precision.
		zStepSize    : distance between slices of the stack, in µm with 0.1 precision.
		"""
		
		if not isPositiveInteger(nSlices):
			raise ValueError("Number of slice must be a strictly positive integer.")
		
		if not isNumber(zStackCenter) or zStackCenter < 0 :
			raise ValueError("zStackCenter must be a positive number.")
		
		if not isNumber(zStepSize) or zStepSize < 0 :
			raise ValueError("zStepSize must be a positive number.")
		
		cmd = "SoftwareAutofocus({:.1f}, {}, {:.1f})".format(zStackCenter, nSlices, zStepSize)
		
		return self._getFloatValue(cmd)

def testRunScript(im):
	im.runScript("C:\\Users\\Administrator\\Desktop\\Laurent\\laurent_test_tcpip.imsf")

## TEST
if __name__ in ['__builtin__', '__main__']:

	# Create an IM instance
	myIM = IM()

	# Loop over functions, calling the getter/is methods first
	for function in dir(myIM):

		if not (function.startswith("get") or function.startswith("is")) :
			continue # skip non getter

		try :
			print(function , " : ", getattr(myIM, function)()) # Get the function object from the name and call it

		# Print the exception and continue the execution
		except Exception as e:
			print(e)

	
	# Error or not, close the socket
	myIM.closeSocket()
	
	"""
	cmd = "GotoXY(30, 30.003)" 
	cmd = "GotoZ(2940.4)" 
	print (myIM.sendCommand(cmd)) # should print None 
	"""