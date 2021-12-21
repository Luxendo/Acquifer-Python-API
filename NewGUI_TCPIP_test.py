"""
Test script for the TCPIP connection.
Start the IM GUI software, deactivate block exernal connection (restart if that was not deactivated)
Then run this script in Fiji (jython) or in a normal python interpreter
"""

import socket, time


class IM(object):
	"""Object representing the IM from ACQUIFER defined with a list of methods to control it."""
	
	def __init__(self, port=6200):
		"""Initialize a TCP/IP socket for the exchange of commands."""
		
		self._socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # IPv6 on latest IM 
		self._socket.connect(("localhost", port))

	def closeSocket(self):
		"""
		Close the socket, making it available to other resources.
		After closing the socket, no commands can be sent anymore via this IM instance. 
		This should be called at the end of external scripts.
		"""
		self._socket.close()
		
	def sendCommand(self, stringCommand):
		"""
		Send a string command to the IM and wait 50ms for processing of the command.
		The command is converted to a bytearray before sending.
		""" 
		self._socket.sendall(bytearray(stringCommand, "ascii"))
		time.sleep(0.05) # wait 50ms, before sending another command (which is usually whats done next, e.g. with getFeedback

	def getFeedback(self, size=256):
		"""Read a value back from the IM after a "get" command."""
		return self._socket.recv(size).decode("ascii")

	def getValueAsType(self, command, cast):
		"""Send a command, get the feedback and cast it to the type provided by the cast function ex: int."""
		self.sendCommand(command)
		return cast(self.getFeedback())
	
	def getIntegerValue(self, command):
		"""Send a command and parse the feedback to an integer value."""
		return getValueAsType(self, command, int)

	def getFloatValue(self, command):
		"""Send a command and parse the feedback to a float value."""
		return getValueAsType(self, command, float)

	def getBooleanValue(self, command):
		"""Send a command and parse the feedback to a boolean value."""
		return getValueAsType(self, command, bool)
		
	def acquire(self, nSlices, zSliceHeight, zStackCenter, saveDirectory=""):
		"""
		Acquire a Z-stack - NOT AVAILABLE IN TCPIP
		zStackCenter in mm, with 0.1 precision.
		If saveDirectory is "", default to DefaultAcquireFolder
		"""
		if saveDirectory:
			cmd = "Acquire({},{},{},{})".format(nSlices, zSliceHeight, zSliceCenter, saveDirectory)
		
		else:
			cmd = "Acquire({},{},{})".format(nSlices, zSliceHeight, zSliceCenter)
		
		self.sendCommand(cmd)

	def openLid(self):
		self.sendCommand("OpenLid()")

	def closeLid(self):
		self.sendCommand("CloseLid()")

	def isLidClosed(self):
		"""Check if the lid is closed."""
		return self.getBooleanValue("LidClosed()")
		
	def isLidOpened(self):
		"""Check if lid is opened."""
		return self.getBooleanValue("LidOpened()")
		
	def isLiveModeActive(self):
		"""
		Check if LiveMode is active.
		LiveMode is needed for IP-commands to work.
		"""
		return self.getBooleanValue("LiveModeActive()")
		
	def getAmbiantTemperature(self):
		"""Return ambiant temperature in celsius degrees."""
		return self.getFloatValue("GetAmbientTemperature(TemperatureUnit.Celsius)")
	
	def getSampleTemperature(self):
		"""Return the sample temperature in celsius degrees."""
		return self.getFloatValue("GetSampleTemperature(TemperatureUnit.Celsius)")

	def getTargetTemperature(self):
		"""Return the target temperature in celsius degrees."""
		return self.getFloatValue("GetTargetTemperature(TemperatureUnit.Celsius)")

	def setTargetTemperature(self, temp):
		"""Set the target temperature to a given value in degree celsius, with 0.1 precision."""
		
		if (temp < 18 or temp > 34):
			raise ValueError("Target temperature must be in range [18;34].")
			
		self.sendCommand( "SetTargetTemperature({:.1f}, TemperatureUnit.Celsius".format(temp) )

	def getNumberOfColumns(self):
		"""Return the number of plate columns."""
		return self.getIntegerValue("GetCountWellsX()")

	def getNumberOfRows(self):
		"""Return the number of plate rows."""
		return self.getIntegerValue("GetCountWellsY()")

	def getObjectiveIndex(self):
		"""Return the currently selected objective-index (1 to 4)."""
		return self.getIntegerValue("GetObjective()")

	def getPositionX(self):
		"""Return the current objective x-axis position in mm."""
		return self.getFloatValue("GetXPosition()")

	def getPositionY(self):
		"""Return the current objective y-axis position in mm."""
		return self.getFloatValue("GetYPosition()")
	
	def getPositionZ(self):
		"""Return the current objective z-axis position in µm."""
		return self.getFloatValue("GetZPosition()")

	def goToXY(self,x,y):
		"""Move to position x,y in mm, with 0.01 decimal precision."""
		cmd = "GotoXY({:.2f},{:.2f})".format(x,y) # force max 2 decimal positions
		self.sendCommand(cmd)

	def goToZ(self, z):
		"""Move to Z-position in µm with 0.1 precision."""
		cmd = "GotoZ({:.1f})".format(z)
		self.sendCommand(cmd)
	
	def goToXYZ(self,x,y,z):
		"""Move to x,y position (mm, 0.01 precision) and z-position in µm (0.1 precision)"""
		cmd = "GotoXYZ({:.2f},{:.2f},{:.1f})".format(x,y,z)
		self.sendCommand(cmd)

	def runScript(self, scriptPath):
		"""
		Start a script.
		This command can be called only if no script is running.
		"""
		cmd = "RunScript({})".format(scriptPath)
		self.sendCommand(cmd)

	def setCamera(self, binning, x, y, width, height):
		
		if binning not in (1,2,4):
			raise ValueError("Binning should be 1,2 or 4.")

		largerThan2048 = lambda value : value > 2048
		negative	   = lambda value : value < 0 
		
		bbox = map(int, (x,y,width,height)) # Make sure they are integer
		
		if any(map(largerThan2048, bbox)) or any(map(negative, bbox)):
			raise ValueError("x,y,width,height must be in range [0;2048]")
		
		self.sendCommand("SetCamera({},{},{},{},{})".format(binning, **bbox))

	def setObjective(self, index):
		"""Set the objective based on the index (1 to 4)."""
		
		if index not in (1,2,3,4):
			raise ValueError("Objective index must be in range [1,4].") 
		
		self.sendCommand( "SetObjective({})".format(index) )
		

## TEST
if __name__ in ['__builtin__', '__main__']:

	# Create an IM instance
	myIM = IM()

	# Loop over functions, calling the getter methods first
	for function in dir(myIM):

		if not function.startswith("get"):
			continue # skip the non getter

		try :
			print function , " : ", getattr(myIM, function)

		except Exception:
			print Exception

	# Error or not close the socket
	myIM.closeSocket()
	
	"""
	cmd = "GotoXY(30, 30.003)"
	cmd = "GotoZ(2940.4)"
	print (myIM.sendCommand(cmd)) # should print None
	"""