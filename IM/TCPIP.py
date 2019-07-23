'''
This module implements the Imaging Machine (IM) class
The class contains a set of funtions to control the IM using TCP/IP
In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging strings of bytes.
Read/Write actions are always preceeded by a first read/write, that sends/read a 4 byte string containing the size of the message to read/write next (use len(byte string message)) to get the decimal value for the weight of the message, convert it to Hex and encode it in a byte string using bytes.fromhex

For new commands, take the "Send Len Hex" and "sent message Hex" decimal code from the labview VI and convert it to a byte using bytes.fromhex(str(hexcode))
'''
import socket, os, sys


class IM(object):
    '''Object representing the IM from ACQUIFER defined with a list of methods to control it'''
    
    
    def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=6261):
        '''Initialise a TCP/IP socket for the exchange of commands'''
        
        # local IP and port (constant)
        self._TCP_IP_ = TCP_IP
        self._TCP_PORT_ = TCP_PORT
        
        # Open a TCP/IP socket to communicate
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
    
    
    def __str__(self):
        '''Return a string representation of the object'''
        return "IM v{} at IP:{}, Port:{}, status:{}".format( self.getVersion(), self._TCP_IP_, self._TCP_PORT_, self.getStatus() )
    
    
    def __getFeedback__(self, size=4):
       '''Generic function to get feedback from the machine after sending a request'''
        
       ## 1st TCP read of 4 bytes to get the size of the message to read
       size_bytes = self.socket.recv(size) # always 4 bytes for the header
       
       # Convert the received size from byte string to decimal
       if sys.version_info.major == 2:
           value = int(size_bytes.encode('hex'), 16)
       
       elif sys.version_info.major == 3:
            value = int.from_bytes(size_bytes, byteorder="big")
            
       ## 2nd TCP actually read the message
       return self.socket.recv(value)
    
    
    def getVersion(self):
        '''Get IM version'''
        
        # send request
        self.socket.send(b'\x00\x00\x00\x18')
        self.socket.send(b'\x02Get\x1fIMVersion\x1f10982031\x03')
        
        # Read feedback and extract version
        out = self.__getFeedback__()
        offset = out.find(b'\x1f')
        Version = out[offset+1:-1].decode("UTF-8")
        
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
        '''Also not functionnal in the VI always return 0'''
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
        
        if X<10 or X>119 or Y<7 or Y>82:
            raise ValueError("X and/or Y is out of the allowed range. Allowed range: X=[10,119], Y=[7,82]")
            
        # Compute the length of the integer part of X and Y (impact size of the string that is sent ex: X=1.2, Y=2.3 -> Length = 2)
        # Max X and Y have each 5 integer digits ex: 10000
        Length = len( str( int(X) ) ) +  len( str( int(Y) ) )
              
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
        self.socket.send(size)
        self.socket.send(b'\x02Command\x1fGotoXYAxis\x1f19901915\x1f' + X + b'\x1f' + Y + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def gotoZ(self,Z):
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
        self.socket.send(size)
        self.socket.send(b'\x02Command\x1fGotoZAxis\x1f1655963\x1f' + Z + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def setScriptFile(self, ScriptPath):
        '''Load a pre-configured .imsf script file'''
        
        # Check file path
        if not os.path.exists(ScriptPath):
            raise FileNotFoundError("No such file at this path")
        
        elif os.path.isdir(ScriptPath):
            raise IsADirectoryError("setScriptFile expects a path to a .scpt file, not a folder")
            
        elif not ( ScriptPath.endswith(".scpt") or ScriptPath.endswith(".imsf") ):
            raise TypeError("setScriptFile expects a path to a .scpt or .imsf file")
            
        # Get size of string to send
        TotalSize = 25 + len(ScriptPath) # 25 (depends on timestamp) is the minimum on top of which len(Path) is added
        size_bytes = bytes.fromhex(format(TotalSize, '08X')) # first dec -> Hex string of defined length (8), then to bytes string
        
        # Encode the Path into a byte string
        BytePath = ScriptPath.encode()
        
        # send command
        self.socket.send(size_bytes)
        self.socket.send(b'\x02Set\x1fScriptFile\x1f2930926\x1f' + BytePath + b'\x03')
        
        # Bump feedback
        self.__getFeedback__()
        

    def startScript(self):
        '''Start a previously defined script (using setScript)'''
       
        # send command
        self.socket.send(b'\x00\x00\x00 ')
        self.socket.send(b'\x02Command\x1fStartScript\x1f1403806682\x03')
        
        # Bump feedback
        self.__getFeedback__()
    
    
    def stopScript(self):
        '''Stop currently executing script'''
        
        # send command
        self.socket.send(b'\x00\x00\x00\x1f')
        self.socket.send(b'\x02Command\x1fStopScript\x1f1403833090\x03')
        
        # Bump feedback
        self.__getFeedback__()
        
        
    def closeSocket(self):
        '''Close TCP/IP port'''
        self.socket.close()