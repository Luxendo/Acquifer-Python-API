'''
This module implements the Imaging Machine (IM) class
The class contains a set of funtions to control the IM using TCP/IP
In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging strings of bytes.
Read/Write actions are always preceeded by a first read/write, that sends/read a 4 byte string containing the size of the message to read/write next

For new commands, take the "Send Len Hex" and "sent message Hex" decimal code from the labview VI and convert it to a byte using bytes.fromhex(str(hexcode))

- For some reason GotoXY(0,0) only goes to (5,5) at min

'''
import socket, os, sys


class IM(object):
    '''Object representing the IM from ACQUIFER defined with a list of methods to control it'''
    
    
    def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=6261):
        '''
        Initialise a TCP/IP socket for the exchange of commands
        '''
        # local IP and port (constant)
        self._TCP_IP_ = TCP_IP
        self._TCP_PORT_ = TCP_PORT
        
        # Open a TCP/IP socket to communicate
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
    
    
    def __getFeedback__(self):
       '''Generic function to get feedback from the machine after sending a request'''
        
       # 1st TCP read to get the size of the message to read
       size_bytes = self.socket.recv(4) # always 4 bytes for the header
       
       if sys.version_info.major == 2:
           size = int(size_bytes.encode('hex'), 16)
       
       elif sys.version_info.major == 3:
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
        '''Query IM status Ready/Busy(=script running)'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x17') # header with size of message to expect
        self.socket.send(b'\x02Get\x1fIMStatus\x1f19487256\x03')
        
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Status = out[offset+1:-1].decode()
        
        return Status
    
    
    def getXaxis(self):
        '''Return the X position of the objective in mm'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x14')
        self.socket.send(b'\x02Get\x1fXAxis\x1f19662438\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        X = float(out[offset+1:-1])
        
        return X
        
    
    def getYaxis(self):
        '''Return the Y position of the objective in mm'''
        
        # Send request
        self.socket.send(b'\x00\x00\x00\x14')
        self.socket.send(b'\x02Get\x1fYAxis\x1f19662438\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Y = float(out[offset+1:-1])
        
        return Y
    
    def getZaxis(self):
        '''Return the Z position of the objective in um'''
        
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
        '''Move objective to position X,Y in mm (max 3 decimal ex:1.111)'''
        
        # Make sure X and Y are not longer than 3 decimal
        X,Y = round(X,3), round(Y,3)
        
        # convert X,Y to byte string
        X = '{:.3f}'.format(X).encode()
        Y = '{:.3f}'.format(Y).encode()
        
        # send command
        self.socket.send(b'\x00\x00\x00)')
        self.socket.send(b'\x02Command\x1fGotoXYAxis\x1f19901915\x1f' + X + b'\x1f' + Y + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def gotoZ(self,Z):
        '''Move objective to position Z in um (max 1 decimal ex:1.1)'''
        
        # Make sure Z is not longer than 1 decimal
        Z= round(Z,1)
        
        # convert Z to byte string
        Z = '{:.1f}'.format(Z).encode()
        
        # send command
        self.socket.send(b'\x00\x00\x00\x1f')
        self.socket.send(b'\x02Command\x1fGotoZAxis\x1f1655963\x1f' + Z + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def setScriptFile(self, ScriptPath):
        '''Load a pre-configured .imsf script file'''
        
        # Turn path into a byte string
        if os.path.exists(ScriptPath):
            BytePath = ScriptPath.encode()
            
            # send command
            self.socket.send(b'\x00\x00\x00@')
            self.socket.send(b'\x02Set\x1fScriptFile\x1f2930926\x1f' + BytePath + b'\x03')
            
            # Bump feedback
            self.__getFeedback__()
        
        else:
            raise FileNotFoundError("The provided Script file.imsf does not exist")
        
        
    def startScript(self):
        '''Start a previously defined script (using setScript)'''
       
        # send command
        self.socket.send(b'\x00\x00\x00\x1d')
        self.socket.send(b'\x02Command\x1fStartScript\x1f2060372\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def stopScript(self):
        '''Stop currently executing script'''
        
        # send command
        self.socket.send(b'\x00\x00\x00\x1c')
        self.socket.send(b'\x02Command\x1fStopScript\x1f2095120\x03')
        
        # Bump feedback
        self.__getFeedback__()
        
        
    def closeSocket(self):
        '''Close TCP/IP port'''
        self.socket.close()
