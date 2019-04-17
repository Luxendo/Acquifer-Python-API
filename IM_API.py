'''
This module implements the Imaging Machine (IM) class
The class contains a set of funtions to control the IM using TCP/IP
In TCP/IP vocabulary this script is on the client side, while the machine controller is the server
The TCP/IP works by exchanging byte strings.
Read/Write actions are always preceeded by a first read/write, setting the size of the "functionnal" command to read or write 

NB : if bugs with some receive commands, round to the next 2^ the number of bytes to read
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
	
	
	def getIMstatus(self):
		# Send request
		self.socket.send(b'\x00\x00\x00\x17')
		self.socket.send(b'\x02Get\x1fIMStatus\x1f19487256\x03')
		
		# Read feedback
		self.socket.recv(4) # size
		out = self.socket.recv(16) 
		
		return out.decode("utf-8")) # TO DO slice to take only the string
	
	
	def getXaxis(self):
		'''Return the X position of the objective in...mm??'''
		
		# Send request
		self.socket.send(b'\x00\x00\x00\x14')
		self.socket.send(b'\x02Get\x1fXAxis\x1f19662438\x03')
		
		# Read feedback
		self.socket.recv(4) # size
		out = self.socket.recv(16)
		
		return out # TO DO slice to take only the coordinates
		
	
	def getYaxis(self):
		'''Return the Y position of the objective in...mm??'''
		
		# Send request
		self.socket.send(b'\x00\x00\x00\x14')
		self.socket.send(b'\x02Get\x1fXAxis\x1f19662438\x03')
		
		# Read feedback
		self.socket.recv(4) # size
		out = self.socket.recv(16)
		
		return out # TO DO slice to take only the coordinates
	
	
	def getZaxis(self):
		'''Return the Z position of the objective in...mm??'''
		
		# Send request
		self.socket.send(b'\x00\x00\x00\x14')
		self.socket.send(b'\x02Get\x1fZAxis\x1f19736510\x03')
		
		# Read feedback
		self.socket.recv(4) # size
		out = self.socket.recv(14)
		
		return out # TO DO slice to take only the coordinates
	
	
	def getWellCoordinates(self):
		# send request
		self.socket.send(b'\x00\x00\x00\x1d')
		self.socket.send(b'\x02Get\x1fWellCoordinate\x1f19813767\x03')
		
		# read feedback
		self.socket.recv(4)
		
		out = self.socket.recv(11)
		
		return out
	
	
	def  getZstackCenter(self):
		# send request
		self.socket.send(b'\x00\x00\x00\x1b')
		self.socket.send(b'\x02Get\x1fZStackCenter\x1f19841627\x03')
		
		# read feedback
		self.socket.recv(4)
		out = self.socket.recv(16)
		
		return out
	
	
	def openLid(self):
		self.socket.send(b'\x00\x00\x00\x1a')
		self.socket.send(b'\x02Command\x1fOpenLid\x1f17248828\x03')
	
	
	def closeLid(self):
		self.socket.send(b'\x00\x00\x00\x1a')
		self.socket.send(b'\x02Command\x1fCloseLid\x1f8809857\x03')
	
	
	def gotoXY(self,X,Y):
		
		# Make sure X and Y are not longer than 3 decimal
		X,Y = round(X,3), round(Y,3)
		
		# convert X,Y to byte string
		X = str(X).encode()
		Y = str(Y).encode()
		
		# send command
		self.socket.send(b'\x00\x00\x00)')
		self.socket.send(b'\x02Command\x1fGotoXYAxis\x1f19901915\x1f' + X +'\x1f' + Y + '\x03')
		
	
	def closeSocket(self):
		self.socket.close()
