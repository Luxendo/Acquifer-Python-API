'''
This private module contains a set of funtions to control the IM using TCP/IP
They are used in the acquifer.__init___ module within the IM class but are stored here
to limit the size of the __init__ file
See test_tcpip.py in the repo's root directory for testing

In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging strings of bytes.
Read/Write actions are always preceeded by a first read/write, that sends/read a 4 byte string containing the size of the message to read/write next (use len(byte string message)) to get the decimal value for the weight of the message, convert it to Hex and encode it in a byte string using bytes.fromhex

For new commands, take the "Send Len Hex" and "sent message Hex" decimal code from the labview VI and convert it to a byte using bytes.fromhex(str(hexcode))

The IM_TCPIP argument in the function below corresponds to an instance of the IM.TCPIP class
'''
import os, sys


def getFeedback(IM_TCPIP, size=4):
	'''Generic function to get feedback from the machine after sending a request'''
	
	## 1st TCP read of 4 bytes to get the size of the message to read
	size_bytes = IM_TCPIP._socket.recv(size) # always 4 bytes for the header
	
	# Convert the received size from byte string to decimal
	if sys.version_info.major == 2:	 value = int(size_bytes.encode('hex'), 16)
	elif sys.version_info.major == 3: value = int.from_bytes(size_bytes, byteorder="big")
		
	## 2nd TCP actually read the message
	return IM_TCPIP._socket.recv(value)

def parseValue(byteString, cast=None):
	"""Extract the string value from the feedback string and optionally cast the resulting string to a predefined type ex: int, float"""
	offset = byteString.find(b'\x1f')      # the value is always between the x1f tag and until the last character, the end tag x3f
	out = byteString[offset+1:-1] 
	
	return cast(out) if cast else out.decode() # decode("UTF-8") or just decode ?

def getFeedbackAndParseValue(IM_TCPIP, cast=None):
	"""Call the feedback and directly parse the value of interest"""
	feedback = getFeedback(IM_TCPIP)
	return parseValue(feedback, cast)

def getVersion(IM_TCPIP):
	'''Get IM version'''
	
	# send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x18')
	IM_TCPIP._socket.send(b'\x02Get\x1fIMVersion\x1f10982031\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP)

def getStatus(IM_TCPIP):
	'''Query IM status Ready/Busy(=script running)'''
	
	# Send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x17') # header with size of message to expect
	IM_TCPIP._socket.send(b'\x02Get\x1fIMStatus\x1f19487256\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP)

def getXaxis(IM_TCPIP):
	'''Return the X position of the objective in mm'''
	
	# Send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x14')
	IM_TCPIP._socket.send(b'\x02Get\x1fXAxis\x1f19662438\x03')
	
	return  getFeedbackAndParseValue(IM_TCPIP, cast=float)

def getYaxis(IM_TCPIP):
	'''Return the Y position of the objective in mm'''
	
	# Send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x14')
	IM_TCPIP._socket.send(b'\x02Get\x1fYAxis\x1f19662438\x03')

	return getFeedbackAndParseValue(IM_TCPIP, float)

def getZaxis(IM_TCPIP):
	'''Return the Z position of the objective in um'''
	
	# Send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x14')
	IM_TCPIP._socket.send(b'\x02Get\x1fZAxis\x1f19736510\x03')

	return getFeedbackAndParseValue(IM_TCPIP, float)

def getObjectiveNo(IM_TCPIP):
	"""Return the number of the current Objective"""
	
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1c')
	IM_TCPIP._socket.send(b'\x02Get\x1fObjectiveNo\x1f1030281479\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP, int)

def getLightNo(IM_TCPIP):
	"""Return the current light channel number 0: none to 6:BF."""
	
	IM_TCPIP._socket.send(b'\x00\x00\x00\x18')
	IM_TCPIP._socket.send(b'\x02Get\x1fLightNo\x1f1032592535\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP, int)

def getWellCoordinates(IM_TCPIP):
	'''Return the well identifier ex:A001 when the acquisition is running exclusively'''
	# send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1d')
	IM_TCPIP._socket.send(b'\x02Get\x1fWellCoordinate\x1f19813767\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP)

def getZstackCenter(IM_TCPIP):
	'''Return the Z-stack center when an acquisition is running exclusively'''
	# send request
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1b')
	IM_TCPIP._socket.send(b'\x02Get\x1fZStackCenter\x1f19841627\x03')
	
	return getFeedbackAndParseValue(IM_TCPIP, float)

def openLid(IM_TCPIP):
	"""Open the IM lid."""
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1a')
	IM_TCPIP._socket.send(b'\x02Command\x1fOpenLid\x1f17248828\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def closeLid(IM_TCPIP):
	"""Close the IM lid."""
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1a')
	IM_TCPIP._socket.send(b'\x02Command\x1fCloseLid\x1f8809857\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def goToXY(IM_TCPIP,X,Y):
	'''Move objective to position X,Y in mm (max 3 decimal ex:1.111)'''
	
	if X<10 or X>119 or Y<7 or Y>82:
		raise ValueError("X and/or Y is out of the allowed range. Allowed range: X=[10,119], Y=[7,82]")
		
	# Compute the length of the integer part of X and Y (impact size of the string that is sent ex: X=1.2, Y=2.3 -> Length = 2)
	# Max X and Y have each 5 integer digits ex: 10000
	Length = len( str( int(X) ) ) +	 len( str( int(Y) ) )
		  
	# Adjust size header according to number of integer digits for X and Y
	# Length = 2 (X has 1 integer digit and Y too) -> Dec=41 - Hex=0000 0029
	# Length = 3 (X has 1 integer and Y 2 or reverse) -> Dec=42 - Hex=0000 002A
	# etc. increase the Dec and check the Hex code
	if Length == 2:
		size = b'\x00\x00\x00)' # Dec=41 - Hex=0000 0029
	
	elif Length == 3:
		size = b'\x00\x00\x00*' # Dec=42 - Hex=0000 002A
	
	elif Length == 4:
		size = b'\x00\x00\x00+' # Dec=43 - Hex=0000 002B
	
	elif Length == 5:
		size = b'\x00\x00\x00,' # Dec=44 - Hex=0000 002C
	
	elif Length == 6:
		size = b'\x00\x00\x00-' # Dec=45 - Hex=0000 002D
	
	elif Length == 7:
		size = b'\x00\x00\x00.' # Dec=46 - Hex=0000 002E
	
	elif Length == 8:
		size = b'\x00\x00\x00/' # Dec=47 - Hex=0000 002F
	
	elif Length == 9:
		size = b'\x00\x00\x000' # Dec=48 - Hex=0000 0030
	
	elif Length == 10:
		size = b'\x00\x00\x001' # Dec=49 - Hex=0000 0031
	
	# Make sure X and Y are not longer than 3 decimal
	X,Y = round(X,3), round(Y,3)
	
	# convert X,Y to byte string
	X = '{:.3f}'.format(X).encode()
	Y = '{:.3f}'.format(Y).encode()
	
	# send command
	IM_TCPIP._socket.send(size)
	IM_TCPIP._socket.send(b'\x02Command\x1fGotoXYAxis\x1f19901915\x1f' + X + b'\x1f' + Y + b'\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def goToZ(IM_TCPIP,Z):
	'''Move objective to position Z in um (max 1 decimal ex:1.1)'''
	
	# Make sure Z is not longer than 1 decimal
	Z= round(Z,1)
	
	
	# Adjust size of the header accordingly
	if Z>=0 and Z<=9.9:
		size = b'\x00\x00\x00\x1f' # Hex = 0000 001F
	
	elif Z>=10 and Z<=99.9:
		size = b'\x00\x00\x00 ' # Hex = 0000 0020
	
	elif Z>=100 and Z<=999.9:
		size = b'\x00\x00\x00!' # Hex = 0000 0021
	
	elif Z>=1000 and Z<=9999.9:
		size = b'\x00\x00\x00"' # Hex = 0000 0022
	
	elif Z>=10000 and Z<=23000:
		size = b'\x00\x00\x00#' # Hex = 0000 0023
	
	else:
		raise ValueError('Z-value out of range')
	
	# convert Z to byte string
	Z = '{:.1f}'.format(Z).encode()
	
	# send command
	IM_TCPIP._socket.send(size)
	IM_TCPIP._socket.send(b'\x02Command\x1fGotoZAxis\x1f1655963\x1f' + Z + b'\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def setScriptFile(IM_TCPIP, ScriptPath):
	'''Load a pre-configured .imsf script file'''
	
	# Check file path
	if not os.path.exists(ScriptPath):
		if sys.version_info.major == 2: FileNotFoundError = IOError # FileNotFoundError does not exist in Py2 
		raise FileNotFoundError("No such file at this path")
			
	elif os.path.isdir(ScriptPath):
		if sys.version_info.major == 2: IsADirectoryError = IOError # IsADirectoryError does not exist in Py2 
		raise IsADirectoryError("setScriptFile expects a path to a .scpt or .imsf file, not to a folder")
		
	elif not ( ScriptPath.endswith(".scpt") or ScriptPath.endswith(".imsf") ):
		raise TypeError("setScriptFile expects a path to a .scpt or .imsf file")
		
	# Get size of string to send
	TotalSize = 25 + len(ScriptPath)				# 25 (depends on timestamp) is the minimum on top of which len(Path) is added
	sizeHex	  = format(TotalSize, '08X')			# dec -> Hex string of defined length (8)
	sizeBytes = bytes( bytearray.fromhex(sizeHex) ) # Hex to bytes string
	
	# Encode the Path into a byte string
	BytePath = ScriptPath.encode()
	
	# send command
	IM_TCPIP._socket.send(sizeBytes)
	IM_TCPIP._socket.send(b'\x02Set\x1fScriptFile\x1f2930926\x1f' + BytePath + b'\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def startScript(IM_TCPIP):
	'''Start a previously defined script (using setScript)'''
	
	# send command
	IM_TCPIP._socket.send(b'\x00\x00\x00 ')
	IM_TCPIP._socket.send(b'\x02Command\x1fStartScript\x1f1403806682\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def stopScript(IM_TCPIP):
	'''Stop currently executing script'''
	
	# send command
	IM_TCPIP._socket.send(b'\x00\x00\x00\x1f')
	IM_TCPIP._socket.send(b'\x02Command\x1fStopScript\x1f1403833090\x03')
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def closeSocket(IM_TCPIP):
	'''Close TCP/IP port'''
	IM_TCPIP._socket.close()