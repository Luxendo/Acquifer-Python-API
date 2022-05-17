from . import tcpip # needed to be able to do from acquifer import tcpip
from .version import __version__

class WellPosition():
	"""
	A WellPosition holds the objective coordinates, for a subposition within a well.
	It also has the reference to the well and subposition, which is used when calling moveXYto(wellPosition).
	"""
	
	def __init__(self, wellID:str, x:float, y:float, subposition:int = 1):
		"""
		Create a new well position
		
		Parameters
		----------
		wellID : str
			wellID as in IM filename, it should start with a capital letter followed by 3 numbers.
		x : float
			Objective coordinates in mm
		y : float
			Objective coordinates in mm.
		subposition : int, optional
			subposition index within a well, this will impact the PO tag in the filename. The default is 1.
		"""
		self.wellID = checkWellID(wellID)
		
		if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
			raise TypeError("x,y must be numbers")
		
		if x<0 or y<0:
			raise ValueError("x,y must be positive.")
		
		error = "Subposition must be a strictly positive integer i.e starting from 1."
		if not isinstance(subposition, int):
			raise TypeError(error)
		
		if subposition < 1:
			raise ValueError(error)
		
		self.x = x
		self.y = y
		self.subposition = subposition


def checkWellID(wellID:str):
	"""
	Raise a ValueError if the wellID is not a 4-character string starting with a capital letter in range A-P, followed by 3 numbers for the plate column.
	The plate column shouldbe in range (1-24) corresponding to the 384 plate format.
	Return
	------
	The wellID if it passes the checks
	"""
	error = "WellID should be a 4-character string, in the form 'A001'"
	if not isinstance(wellID, str):
		raise TypeError(error)
	
	if len(wellID) != 4:
		raise ValueError(error)
	
	asciiValueRow = ord(wellID[0])
	if asciiValueRow < 65 or asciiValueRow > 80 :
		raise ValueError("WellID should start with a capital letter in range A-P.")
	
	if not wellID[1:].isdecimal():
		raise ValueError("The WellID should start with a capital letter in range A-P, followed by 3 numbers.")
	
	column = int(wellID[1:])
	if column < 1 or column > 24:
		raise ValueError("Plate column {} out of range [1-24]".format(column))
	
	return wellID
	