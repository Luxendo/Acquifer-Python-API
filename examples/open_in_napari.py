"""
This example will prompt for an IM dataset directory and display it as a multi-dimensional array in napari.
Data loading use the dask-image library, which use lazy-loading, similar to the VirtualStack of ImageJ to load the images "on request"

For this example to work you need to install napari in the python environment running the example.
With pip : 
    pip install napari[all]
"""
from acquifer_napari_plugin.utils import array_from_directory
import napari

def view_in_napari(array6D):
    """
    Helper function to view a xarray in napari.
    The array is generated with the function array_from_directory from the acquifer.utils module .
    
    The xarray is expected to have 6 dimensions in the order channel-well-time-z with the associated labels.
    """
    # Define constants for viewing
    DEFAULT_CHANNEL_COLORS = ["cyan", "green","yellow", "red", "magenta", "gray"] # ordered from CO1 to CO6
    
    listNames     = [] # as shown in left channel-panel in napari, default Cx with x in [1,6]
    listColormaps = [] # color map/LUT for the channels
    listOpacities = [] # default opacities (1 for BF, 0.5 for Fluo to hava good blend)
    for channel in array6D["Channel"].values:
        listNames.append( "C" + str(channel) )
        listColormaps.append( DEFAULT_CHANNEL_COLORS[channel-1] ) # channel-1 since IM-channels are 1-based while positional-indexes are 0-base
        listOpacities.append( 1 if channel==6 else 0.5)
    
    # Image layers are sorted from bottom to top in the image layer panel of napari
    # ie C6 is at the top, and channel names and colormaps are also ordered from 1 to 6
    viewer = napari.view_image(array6D,
                               channel_axis = 0,
                               name     = listNames,
                               colormap = listColormaps,
                               opacity  = listOpacities
                               #axis_labels = dataArray.dims # this one does not work
                               )
    
    viewer.dims.axis_labels = array6D.dims # alternative

### MAIN ###
#%% Ask for a directory and load it as a multi-dimensional dask array
dataset_directory = input("Path to an IM dataset directory : ")
dataset_array = array_from_directory(dataset_directory)

#%% View in napari
view_in_napari(dataset_array)