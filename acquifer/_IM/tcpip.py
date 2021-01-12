'''
This private module contains a set of funtions to control the IM using TCP/IP
They are used in the acquifer.__init___ module within the IM class but are stored here
to limit the size of the __init__ file.
This means every command functions here should have an equivalent in the __init__ module, more precisly in the IM.TCPIP class
See test_tcpip.py in the repo's root directory for testing

In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging strings of bytes.
Read/Write actions are always preceeded by a first read/write, that sends/read a 4 byte string containing the size of the message to read/write next (use len(byte string message)) to get the decimal value for the weight of the message, convert it to Hex and encode it in a byte string using bytes.fromhex

For new commands, take the "Send Len Hex" and "sent message Hex" decimal code from the labview VI and convert it to a byte using bytes.fromhex("hexcode") ex: bytes.fromhex("0000 001F")

For commands taking a string argument ex: setScriptFile(filePath): 
	1) set the path to an empty argument and call the VI function (press the button)
	2) Write down the hex code for "Send len hex" AND "sendStringHex"
	3) Convert (online converter) this code to a decimal value 0000 001F -> 31
	4) When an argument is provided, the len will be the value above (offset) + len(stringArgument) ex: 31 + len("test")
	The offset is specific to the current sendStringHex, which length varies due to a timestamp. 
	A given timestamp can be reused though, ie the offset too.
	5) The function should thus compute the length of the message with the offset and argument
	6) Convert the message length to hexadecimal code string of length 8, using format(size, '08x') 
	7) Convert the hexadecimal code string to a hexadecimal byteString with bytes( bytearray.fromhex(sizeHex) )
	8) Send this byteString for the message length
	9) Convert the sendStringHex from 2) to a byteString using bytes( bytearray.fromhex(sendStringHex) )
	10) Edit this string, by inserting the string argument between the /x01f and /x03f tags, and encoding the stringARgument as byte using stringArgument.encode()
	
	Might be possible to convert directly from decimal to bytes string ex: bytearray([31]) but this does not allow setting the length of the message to 4
	
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

def getBytesLength(baseLength, stringArgument):
	"""Return a byte string communicating the length of a message, provided the message base length (an integer, everything except the argument) and a custom string argument."""
	length    = baseLength + len(stringArgument)
	lengthHex = format(length, '08X')            # decimal to Hexadecimal string of predefined length (8) ex "0000001F"
	return bytes( bytearray.fromhex(lengthHex) ) # Hexadecimal string to bytes string

def sendStringCommand(IM_TCPIP, baseLength, commandPrefix, stringArgument):
	"""
	Send a command with custom string argument to the IM.
	baseLength     : int, length of the message without stringArgument
	commandPrefix  : byteString, string for the message without the last \x03 tag, it should be the command corresponding to the baseLength
	stringArgument : string, custom argument to path ex: a plate name. 
	"""
	sizeBytes = getBytesLength(baseLength, stringArgument)
	IM_TCPIP._socket.send(sizeBytes)
	IM_TCPIP._socket.send(commandPrefix + stringArgument.encode() + b'\x03')

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

def setScriptFile(IM_TCPIP, scriptPath):
	'''Load a pre-configured .imsf script file'''
	
	# Check file path
	if not os.path.exists(scriptPath):
		if sys.version_info.major == 2: FileNotFoundError = IOError # FileNotFoundError does not exist in Py2 
		raise FileNotFoundError("No such file at this path")
			
	elif os.path.isdir(scriptPath):
		if sys.version_info.major == 2: IsADirectoryError = IOError # IsADirectoryError does not exist in Py2 
		raise IsADirectoryError("setScriptFile expects a path to a .scpt or .imsf file, not to a folder")
		
	elif not ( scriptPath.endswith(".scpt") or scriptPath.endswith(".imsf") ):
		raise TypeError("setScriptFile expects a path to a .scpt or .imsf file")
		
	sendStringCommand(IM_TCPIP, 25, b'\x02Set\x1fScriptFile\x1f2930926\x1f', scriptPath )
	
	# Bump feedback
	getFeedback(IM_TCPIP)

def setProject(IM_TCPIP, projectName):
	"""Set the project name (string), corresponds to set Script Project in the VI."""
	sendStringCommand(IM_TCPIP, 31, b'\x02Set\x1fScriptProject\x1f1091397111\x1f', projectName)
	getFeedback(IM_TCPIP)

def setPlate(IM_TCPIP, plateName):
	"""Set the plate name (string), corresponds to set Script Plate Name in the VI."""
	sendStringCommand(IM_TCPIP, 33, b'\x02Set\x1fScriptPlateName\x1f1093819124\x1f', plateName)
	getFeedback(IM_TCPIP)

def startScript(IM_TCPIP):
	'''Start a previously defined script (using setScriptFile)'''
	
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