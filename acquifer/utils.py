"""
This module provides a set of utility functions when working with IM datasets.
It includes loading IM datasets as multi-dimensional array in python...
"""
from dask_image.imread import imread
from sortedcontainers import SortedSet
import os
import numpy as np
import dask.array as da
import xarray as xr
from . import metadata
from typing import List

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



DataArray = xr.core.dataarray.DataArray # this is just a type-alias used in function signature (shorter than the full thing)

def array_from_directory(directory: str) -> DataArray:
    return array_from_imagelist(os.listdir(directory), directory)

def array_from_imagelist(list_images : List[str], directory:str = None) -> DataArray:
    """
    Create a 6-dimensional xarray backed by a Dask array from an IM directory.  
    This is mostly used as a way to load images in napari.
    
    list_images : list of strings
    ============================
    Either a list of filenames if directory is specified, or directly the image filepaths if directory is None
    
    directory
    ========
    Path to a directory containing the file mentioned in list_images, or None (default) if the list_images is already the full filepaths
    
    The dask array uses lazy-loading for computation and visualization of the images.
    The dimensions order is as following channel-well-time-z.
    
    The xarray allows labeling the dimensions, and the value along the dimensions (well names, channels...) 
    Use .values on the array to recover a numpy array.
    
    Each channel is represented as a separate dask array with Well, T, and Z components.
    The reason is that when representing a dask array in napari, all slices of the array use the same Look Up Table.
    That's why we make a large dask array with dimension orderer Channel-Well-T-Z

    Dask uses lazy loading by default, which allows fast visualization of large dataset.
    Each IM image (ie image-plane) is a 2D dask array, itself contained in a larger dask array for the current dimension.
    By stacking the dasks array for the sub-dimensions one can achieve a multi-dimensional dask array.
    The stacking of dask-arrays is an alternative to the currently not supported reshaping of a single dask array with all iamges.
    Described here https://napari.org/stable/tutorials/processing/dask.html
    """
    if directory : 
        list_filepaths = [os.path.join(directory, filename) for filename in list_images]
    else:
        list_filepaths = list_images
                      
    # First full loop pass on the dataset to identify the size of the dataset and of each dimensions 
    # Find unique well, and CZT in this dataset
    # Sorted since we use those sets for ordering of the image in the nD-array
    setChannels = SortedSet()
    setWells    = SortedSet()
    setT        = SortedSet()
    setZ        = SortedSet()
    
    for filepath in list_filepaths:
        filename = os.path.basename(filepath)
        
        setChannels.add( metadata.getChannelIndex(filename) )
        setWells.add( metadata.getWellId(filename) )
        setT.add( metadata.getTimepoint(filename) )
        setZ.add( metadata.getZSlice(filename) )
    
    # Create an empty numpy array of shape [nC][nWells][nT][nZ]
    # It will be filled with the filepath for the corresponding plane
    shape = (len(setChannels),
             len(setWells),
             len(setT),
             len(setZ))
    
    filepathArray = np.empty(shape, dtype=object) # dont use dtype str here
    
    # Fill the numpy array with the image filepaths
    # the positional indexes are recovered from the position of the matching dimension value in the sorted sets
    for filepath in list_filepaths:
        filename = os.path.basename(filepath)

        imageC    = metadata.getChannelIndex(filename)
        imageWell = metadata.getWellId(filename)
        imageT    = metadata.getTimepoint(filename)
        imageZ    = metadata.getZSlice(filename) 
        
        # Put filepath for corresponding plane in the array
        # Plane position in the array given by index from sets above
        filepathArray[setChannels.index(imageC)] \
                     [setWells.index(imageWell)] \
                     [setT.index(imageT)] \
                     [setZ.index(imageZ)] = filepath
    
    
    # Turn the nD-numpy array to a nD-Dask array
    # The nD dask array is made by first reading each image into a single plane dask array
    # and by then stacking each dask array for each dimensions
    listChannels = []
    for channel in filepathArray:
        
        listWells = []
        for well in channel:
            
            listTime = []
            for timepoint in well:
                
                listZ = []
                for zSlice in timepoint:
                    listZ.append( imread(zSlice) ) # dask.imread is lazy by default
                
                listTime.append( da.concatenate(listZ) ) # here use concatenate not stack since we extend the 3rd dimension, we dont want to add another dimension
            
            # Turn listTime into a stacked dask array and append to upper level list
            listWells.append(da.stack(listTime))
            
        listChannels.append(da.stack(listWells))
    
    mainArray = da.stack(listChannels)
    
    return xr.DataArray(mainArray, 
                        dims=["Channel", "Well", "Time", "Z", "Y", "X"],
                        coords={"Channel": setChannels, # define discrete values available on this dimension
                                "Well":    setWells,
                                "Time" :   setT,
                                "Z":       setZ} )