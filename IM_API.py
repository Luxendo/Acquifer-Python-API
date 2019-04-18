'''
This module implements the Imaging Machine (IM) class
The class contains a set of funtions to control the IM using TCP/IP
In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging strings of bytes.
Read/Write actions are always preceeded by a first read/write, setting the size in bytes of the "functionnal" command to read or write
This size is apparently constant (to check if the timestamp in the message is not increasing the length)
 
NB : if bugs with some receive commands, round to the next 2^ the number of bytes to read

For new commands, take the "Send Len Hex" decimal code and convert it to a byte using bytes.fromhex(str(hexcode))
'''
import socket


class IM(object):
    
    def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=6261):
        '''
        Initialise a TCP/IP socket for the exchange of commands
        '''
        # local IP and port (constant)
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        
        # Open a TCP/IP socket to communicate
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
    
    def __getFeedback__(self):
       '''Generic function to get feedback from the machine after sending a request'''
        
       # 1st TCP read to get the size of the message to read
       size_bytes = self.socket.recv(4) # always 4 bytes for the header
       size = int.from_bytes(size_bytes, byteorder="big")
        
       # 2nd TCP read actually reading the message
       return self.socket.recv(size)
    
    
    def getVersion(self):
        '''Get IM version'''
        
        # send request
        self.socket.send(b'\x00\x00\x00\x18')
        self.socket.send(b'\x02Get\x1fIMVersion\x1f10982031\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Version = float(out[offset+1:-1])
        
        return Version 
        
   
    def getStatus(self):
        '''Query IM status Ready/?Busy?'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x17') # header with size of message to expect
        self.socket.send(b'\x02Get\x1fIMStatus\x1f19487256\x03')
        
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Status = out[offset+1:-1].decode()
        
        return Status
    
    
    def getXaxis(self):
        '''Return the X position of the objective in...mm??'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x14')
        self.socket.send(b'\x02Get\x1fXAxis\x1f19662438\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        X = float(out[offset+1:-1])
        
        return X
        
    
    def getYaxis(self):
        '''Return the Y position of the objective in...mm??'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x14')
        self.socket.send(b'\x02Get\x1fYAxis\x1f19662438\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Y = float(out[offset+1:-1])
        
        return Y
    
    def getZaxis(self):
        '''Return the Z position of the objective in...mm??'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x14')
        self.socket.send(b'\x02Get\x1fZAxis\x1f19736510\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Z = float(out[offset+1:-1])
        
        return Z
    
    
    def getWellCoordinates(self):
        '''Not functionnal in the VI'''
        # send request
        self.socket.send(b'\x00\x00\x00\x1d')
        self.socket.send(b'\x02Get\x1fWellCoordinate\x1f19813767\x03')
        
        return self.__getFeedback__()
    
    
    def getZstackCenter(self):
        # send request
        self.socket.send(b'\x00\x00\x00\x1b')
        self.socket.send(b'\x02Get\x1fZStackCenter\x1f19841627\x03')
        
        # Read feedback and isolate value
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Zcenter = float(out[offset+1:-1])
        
        return Zcenter
    
    
    def openLid(self):
        self.socket.send(b'\x00\x00\x00\x1a')
        self.socket.send(b'\x02Command\x1fOpenLid\x1f17248828\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def closeLid(self):
        self.socket.send(b'\x00\x00\x00\x1a')
        self.socket.send(b'\x02Command\x1fCloseLid\x1f8809857\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def gotoXY(self,X,Y):
        '''Move objective to position X,Y in mm'''
        
        # Make sure X and Y are not longer than 3 decimal
        X,Y = round(X,3), round(Y,3)
        
        # convert X,Y to byte string
        X = str(X).encode()
        Y = str(Y).encode()
        
        # send command
        self.socket.send(b'\x00\x00\x00)')
        self.socket.send(b'\x02Command\x1fGotoXYAxis\x1f19901915\x1f' + X + b'\x1f' + Y + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
        
        
    def closeSocket(self):
        '''Close TCP/IP port'''
        self.socket.close()