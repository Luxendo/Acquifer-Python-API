# IM-Python-API

This repo contain the python module with the IM class to control the machine from a python script using the TCP/IP interface

# Missing functionnalities:
- set and get Objective()
- IncrementX,Y(step) : like the action of clicking the arrow in the GUI. See if available in labview otherwise hrdcoded in python
- setLight(Channel, Intensity, mode) # Mode Flash or continuous
- getWellCoordinates() in live mode
- gotoWell(xx) 
- get/setZstackCenter(Zcenter) in live mode
- snap(ExposureTime) -> returning the image as a matrix would be best (by pointing to a file or a temporary file/memory buffer)
- capture(duration, exposureTime) # for video
- zFocus = AF(ZstackCenter, nSlice, dSlice) # add to table...
- definePlate or defineGrid

# TO DO:
- Automatic metadata setting for file names (should be automatic in the GUI too)    
- once gotoWell is implemented create a class __Plate__ and __Well__ (or a simple dictionnary for well) that would expose an iterator to loop over well positions in order to do    
- Add a nacro tools set to set the scale bar automatically for the IM images (similar to the scale ba tool of Gilles Carpentier http://image.bio.methods.free.fr/ImageJ/?Scale-Bar-Tools-for-Microscopes.html)
``` 
for well in Plate:   
	X = well['X'] or well.X (if using a class)
```
