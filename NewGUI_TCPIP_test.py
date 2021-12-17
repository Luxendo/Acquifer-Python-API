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


## TEST
# Create an IM instance and call a test function
myIM = IM()

cmd = "GotoXY(30, 30.003)"
cmd = "GotoZ(2940.4)"
print (myIM.sendCommand(cmd)) # should print None

time.sleep(0.05) # wait 50ms

#print (myIM.getFeedback())

myIM._socket.close()