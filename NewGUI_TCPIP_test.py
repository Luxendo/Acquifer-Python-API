"""
Test script for the TCPIP connection.
Start the IM GUI software, deactivate block exernal connection (restart if that was not deactivated)
Then run this script in Fiji (jython) or in a normal python interpreter
"""

import socket, time


class IM(object):
    '''Object representing the IM from ACQUIFER defined with a list of methods to control it'''
    
    def __init__(self, port=6200):
        '''Initialise a TCP/IP socket for the exchange of commands'''
        
        self._socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # IPv6 on latest IM 
        self._socket.connect(("localhost", port))
        
    def sendCommand(self, stringCommand):
        """
        Send a string command to the IM.
        The command is converted to a bytearray before sending
        """ 
        self._socket.sendall(bytearray(stringCommand, "ascii"))
        time.sleep(0.05) # wait 50ms, before sending another command (which is usually whats done next, e.g. with getFeedback

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