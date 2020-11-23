"""
This file allows the syntax 
from acquifer import IM, IM03, IM04
In particular IM is the default implementation, the mother class for IM03 and IM04
Therefore only what differs between IM03 and IM04 needs rewriting

Besides the classes are nested with inner classes such as Metadata to allow
IM.Metadata.getWellName()

To reduce the length of this single file, the method bodies are separated in private submodules
which are imported at the top of this script
"""

class IM(Object):
	"""Mother class of all IMs: implement default behaviour"""
	
	def init(self):
		
		
		
	class Metadata():
		
		
		
		
	
class IM03(IM):
	
	class Metadata(IM.Metadata):
		
		def test:
			_metadata.test() # the function would be wrapped in another package for simplicity
			
	class TCPIP(IM.TCPIP)