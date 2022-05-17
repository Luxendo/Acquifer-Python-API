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