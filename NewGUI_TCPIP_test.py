"""
Test script for the TCPIP connection.
Start the IM GUI software, deactivate block exernal connection (restart if that was not deactivated)
Then run this script in Fiji (jython) or in a normal python interpreter
"""

import socket, os, sys, time


class IM():
    '''Object representing the IM from ACQUIFER defined with a list of methods to control it'''
    
    def __init__(self, TCP_PORT=6200):
        '''Initialise a TCP/IP socket for the exchange of commands'''
  
        self._TCP_IP  = socket.gethostbyname("localhost") # resolve to 127.0.0.1 typically
        self._TCP_PORT = TCP_PORT
        
        # Open a TCP/IP socket to communicate
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect( (self._TCP_IP, self._TCP_PORT) )

    def sendCommand(self, stringCommand):
    	return self._scoket.sendall(bytearray(stringCommand, "ascii"))

	def getFeedback(self, size=256):
		return self._socket.recv(size).decode("ascii")


def toByteArray(cmd):
	"""Convert a string command to a byte array compatible with TCPIP communication"""
	return bytearray(cmd, "ascii")


# Create an IM instance and send a test command
myIM = IM() # fails
#myIM = IM(6261)

print( myIM.sendCommand("GetObjective()") ) # should print None

time.sleep(0.05) # wait 50ms

print(myIM.getFeedback())

myIM._socket.close()