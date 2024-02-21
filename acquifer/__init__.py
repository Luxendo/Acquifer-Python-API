from . import tcpip, utils, metadata # scripts excluded to avoid issue when importing clr/pythonnet in spyder # needed to be able to do from acquifer import tcpip, utils, metadata
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
			wellID as in IM filename (but not case sensitive), it should start with a letter followed by 3 numbers.
		
		x : float
			Objective coordinates in mm
		
		y : float
			Objective coordinates in mm.
		
		subposition : int, optional
			subposition index within a well, this will impact the PO tag in the filename. The default is 1.
		"""
		self.wellID = utils.checkWellID(wellID.upper())
		
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