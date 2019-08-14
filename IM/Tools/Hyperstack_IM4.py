'''
HYPERSTACK GENERATOR in Fiji 
Read all tif images from an experiment inFolder that contains tif images for the different wells, channel, slices and timepoints 
The script will automatically reads the field from the filename (using index in the string - FOLLOWING ACQUIFER-IM04 NAMING CONVENTION ex: -A001--...) to generate the well's stack
Images are supposed to be untouched (same sizes, original names).
 
TO DO :  
- Make plate montage for each time point and/or Z-slice with slider that update the full plate display  
 
'''
#@ PrefService prefs
#@ ImageJ imagej
import os, ij 
from ij			      import IJ, VirtualStack 
from ij.plugin 		  import HyperStackConverter,ZProjector 
from ij.WindowManager import getCurrentImage, getCurrentWindow 
from fiji.util.gui	  import GenericDialogPlus 
from java.awt.event   import ActionListener 
from loci.formats 	  import ChannelSeparator  # builtin in Fiji 
 
def dimensionsOf(path): 
  '''Helper function: get dimension of an image without opening it by reading the tif header''' 
  fr = None   
  try:   
	fr = ChannelSeparator()   
	fr.setGroupFiles(False)   
	fr.setId(path)   
	return fr.getSizeX(), fr.getSizeY()   
  except:   
	# Print the error, if any   
	print sys.exc_info()   
  finally:   
	fr.close() 
	 
	 
class ButtonClic(ActionListener): # extends action listener 
	'''Class which unique task is to handle button clics'''  
	 
	def actionPerformed(this, event): 
		'''Called when any of the button is called''' 
		global Win
		
		Source = event.getSource()
		
		if Source.label == "Select all":
			for checkbox in Win.getCheckboxes()[-96:]:  
				checkbox.setState(True)
		
		elif Source.label == "Select none":
			for checkbox in Win.getCheckboxes()[-96:]:  
				checkbox.setState(False)
				
 
# Recover input from persistence 
Path0	= prefs.get("ImageDirectory","MyPath") 
 
Channel0 = prefs.get("Channels","")   
Slice0   = prefs.get("Slices","")  
Time0	 = prefs.get("Times","") 
 
ShowStack0  = prefs.getInt("ShowStack",True) 
SaveStack0  = prefs.getInt("SaveStack",False) 
 
doProj0	     = prefs.getInt("doProj", False)
ProjMethod0  = prefs.get("ProjMethod","max") 
ShowProj0	 = prefs.getInt("ShowProj",False) 
SaveProj0	 = prefs.getInt("SaveProj",False)

BoolWells0   = map(eval, prefs.getList(imagej.class, "BoolWells") )

# Input GUI window   
Win = GenericDialogPlus("Hyperstack generator") # Title of the window 

# Add Acquifer Logo image
LogoPath = os.path.join(IJ.getDirectory("ImageJ"), "lib", "Acquifer_Logo.png")
Logo     = IJ.openImage(LogoPath)
Win.addImage(Logo)

Win.addDirectoryField("Image directory", Path0) 
 
Win.addStringField("Use specific channel(s) separated by , (from 1 to 6) :", Channel0) 
Win.addStringField("Use specific Z-slice(s):", Slice0) 
Win.addStringField("Use specific timepoint(s) separated by ',' :", Time0) 
 
Win.addCheckbox("Show stack ?", ShowStack0) 
Win.addCheckbox("Save stack ?", SaveStack0) 
 
Win.addCheckbox("Make Z-projection ?",doProj0)
Win.addToSameRow()
Win.addChoice("Method",['avg','sd','max','min','sum','median'], ProjMethod0) 
Win.addToSameRow() 
Win.addCheckbox("Show projection ?",ShowProj0) 
Win.addToSameRow() 
Win.addCheckbox("Save projection ?",SaveProj0) 
 
 
# Generate tick box with plate layout to select well 
Wells = [] 
for letter in ['A','B','C','D','E','F','G','H']: 
	for column in range(1,13): 
		Wells.append(letter+'%(column)03d' %{"column":column}) # force max 3 digits and leading 0 

BoolWells0 = [True]*96 if not BoolWells0 else BoolWells0 # 1st run peristence is empty hence we initialise with True
Win.addCheckboxGroup(8,12,Wells, BoolWells0)             # Add result from persistence here 
 
Win.addButton('Select all' , ButtonClic() ) # add an instance of our ButtonClic listener class to the button. Button clicked -> event -> call actionPerformed(event) 
Win.addButton('Select none', ButtonClic() ) 

Disclaimer = "https://doi.org/10.5281/zenodo.3368135"	# Help button should point to the Zenodo page
Win.addHelp(Disclaimer)

Win.addMessage("This plugin is freely provided by ACQUIFER.")

doiPath = os.path.join(IJ.getDirectory("ImageJ"), "lib", "BadgeDOI_Hyperstack.png")
DOI=IJ.openImage(doiPath)
Win.addImage(DOI)

Win.showDialog() 
 
 
 
## Recover input 
if (Win.wasOKed()):  
	inFolder	  = Win.getNextString() 
	Bool		  = [checkbox.getState() for checkbox in Win.getCheckboxes()] 
	 
	ChoiceChannel = Win.getNextString()  
	ChoiceSlice	  = Win.getNextString() 
	ChoiceTime	  = Win.getNextString() 
 
	i=0 
	ShowStack	 = Bool[i] 
	 
	i+=1 
	SaveStack	 = Bool[i] 
	 
	i+=1 
	doProj		 = Bool[i]
	ProjMethod 	 = Win.getNextChoice()
	i+=1 
	ShowProj	 = Bool[i] 
	 
	i+=1 
	SaveProj 	 = Bool[i]	 
 
	i+=1 
	BoolWells	 = Bool[i:]  
	Selection	 = {well:choice for well,choice in zip(Wells,BoolWells)} # create a dictionnary associating a well to a boolean . Chosen or not 
	#print Selection 
	#print len(Wells) # OK 96 
 
	 
	# Save input into memory/persistence 
	prefs.put("ImageDirectory",inFolder) 
	 
	prefs.put("Channels", ChoiceChannel)  
	prefs.put("Slices", ChoiceSlice) 
	prefs.put("Times", ChoiceTime) 
 
	prefs.put("ShowStack", ShowStack) 
	prefs.put("SaveStack", SaveStack) 
 	
	prefs.put("doProj", doProj)
	prefs.put("ProjMethod", ProjMethod) 
	prefs.put("ShowProj", ShowProj) 
	prefs.put("SaveProj", SaveProj)
	
	prefs.put(imagej.class, "BoolWells", map(str, BoolWells) ) # persitence for list works with string only
	 
	# Stop execution if no well selected 
	if BoolWells == [False]*96: 
		IJ.error("No well selected") 
 
	# Reformat input to list after the input has been saved in memory 
	ChoiceChannel = map(int, ChoiceChannel.split(",") ) if ChoiceChannel else []
	ChoiceTime	  = map(int, ChoiceTime.split(",") )	if ChoiceTime	else []
	ChoiceSlice   = map(int, ChoiceSlice.split(",") )   if ChoiceSlice   else [] 
	
	# Find image files for the given channel 
	#inFolder = str(inFolder) # convert filename object to string object 
	WellList	= [] # full list of well to know how many iteration for stacking 
	TimeList	= [] 
	ChannelList = [] 
	SliceList   = [] 
	MainList	= [] # contains tuple with (Filename, Well, TimePoint, Channel, Z-Slice) 
 
	for fname in os.listdir(inFolder): # extract metadata from image filename  
		if fname.endswith(".tif"): 
 
			# first extract the well field 
			Well = fname[1:5] 
 
			# if well is selected in the gui, then extract the other metadata 
			if Selection[Well]: 
 
				try : # int conversion throw an error if the argument string is empty, hence the try  
					Time 	= int(fname[15:18]) 
					Channel = int(fname[22:23]) 
					Slice 	= int(fname[27:30])  
				except : 
					IJ.error("Could not get experimental parameters from filename. Check filename pattern (IM04 convention)") 
					#raise Exception("Could not get experimental parameters from filename. Check filename pattern (IM04 convention)") 
				 
				WellList.append(Well) 
 
				 
				## Channel 
				if ChoiceChannel==[]: # No precise channel specified: We add this particular channel to the list 
					ChannelList.append(Channel) 
					 
				elif Channel in ChoiceChannel: # This particular channel was selected
					ChannelList.append(Channel) 
 
				else: # This particular channel was not selected 
					continue 
 
					 
				 
				## Time 
				if ChoiceTime==[]: # No precise time specified: We add this particular time to the list
					TimeList.append(Time) 
					 
				elif Time in ChoiceTime: # This particular timepoint was selected
					TimeList.append(Time) 
 
				else: # This particular timepoint was not selected
					continue 
				 
 
				 
				## Z-Slice 
				if ChoiceSlice==[]: # No precise slice specified: We add this particular time to the list
					SliceList.append(Slice) 
					 
				elif Slice in ChoiceSlice: # This particular slice was selected
					SliceList.append(Slice) 
 
				else: # This particular timepoint was not selected
					continue 
 
				 
				# Append to main list only if it managed to pass the previous if (thanks to the continue statement) 
				MainList.append((fname,Well,Time,Channel,Slice)) 
 
			 
			else : # the well was not selected in the GUI, go for the next image filename 
				continue 
 
			 
	if len(MainList) < 1: 
		IJ.error("No image files found in %s satisfying the channel/slice/time selection. Check if extension match and if filenames match IM04 naming convention" % inFolder) 
		#raise Exception("No image files found in %s satisfying the channel/slice/time selection. Check if extension match and if filenames match IM04 naming convention" % inFolder) 
 
	# Sort list to prepare iteration 
	WellList = list(set(WellList)) # turn to a set object to have unique item once only  
	WellList.sort() 			   # sort should be after set since set may change order  
 
	TimeList = list(set(TimeList))  
	TimeList.sort() 			   
 
	ChannelList = list(set(ChannelList))  
	ChannelList.sort() 
 
	SliceList = list(set(SliceList))  
	SliceList.sort()  
 
	# Verification 
	print 'Well  : ', WellList 
	print 'Time  : ', TimeList 
	print 'ChannelIdx  : ', ChannelList 
	print 'Z-Slice : ' , SliceList 
 
 
	MainList.sort(key = lambda field:(field[1], field[2], field[4], -field[3]) ) # sort by Well, Time, Z-slice then Channel (- to have C06 ie BF first) since the hyperstack is created following the default "xyczt" order 
	'''
	for i in MainList : 
		print i 
	'''
	 
	# Initialise HyperStackConverter 
	HyperStacker = HyperStackConverter()  
	 
	## Loop over wells to do stack and projection 
	for well in WellList: # - TO DO: Add another level in MainList : one per well 
 
		# Gather images for a given well, and put them into a sublist 
		IJ.showStatus('Process well : '+well+'...') 
		SubList = [item for item in MainList if item[1]==well] # Sublist containing (fname1,Well,Time1,ChannelX,Slice),(fname2,Well,Time2,ChannelX,Slice)  for one given well ex: only A001  
		#print 'StackSize : ',len(SubList) 
		 
		# Get image dimensions of the first image in the list to initialise VStack 
		width, height = dimensionsOf( os.path.join(inFolder,SubList[0][0]) ) 
		 
		# Initialise Virtual Stack for this well 
		VStack = VirtualStack(width, height, None, inFolder)   
		 
		# Append slices in the VStack 
		for item in SubList: 
			filename = item[0] 
			VStack.addSlice(filename) # conversion to ImageProcessor object to append to stack 
	 
			# Once we have finished appending slices, we reconvert back to an ImagePlus object to be able to show and save it 
			ImpStack = ij.ImagePlus(well, VStack) # well is the title of this hyperstack - Reminder : 1 hyperstack/well 
			#print ImpStack 
			#Stack.show() # Good 
		 
		 
		## Make a hyperstack out of the ImagePlus virtual stack 
		if ImpStack.getStackSize()==1:  
			HyperStack = ImpStack # issue when a single slice in the Hyperstack 
		else: 
			HyperStack = HyperStacker.toHyperStack(ImpStack,len(ChannelList), len(SliceList), len(TimeList),"xyczt","grayscale") # convert PROPERLY ORDERED Stack to Hyperstack  
		 
		 
		## Display resulting stack 
		if ShowStack :  
			HyperStack.show() 
		 
		 
		## Save resulting stack 
		if SaveStack : 
			outFolder = os.path.join(inFolder,'HyperStack') 
			if not os.path.exists(outFolder): os.makedirs(outFolder) # create folder if it does not exist (for the first image to save basicly) 
			 
			outPath = os.path.join(outFolder,well+'.tif') 
			IJ.save(HyperStack,outPath)		 
		 
		 
		## PROJECTION 
		if doProj :
			IJ.showStatus('Do projection')
			Projected = ZProjector.run(HyperStack, ProjMethod) 
		 
			# Display projection (automatic with the stack focuser) 
			if ShowProj: 
				Projected.show() 
 
			 
			# Save projection 
			if SaveProj: 
				outFolder = os.path.join(inFolder,'Projected') 
				if not os.path.exists(outFolder): os.makedirs(outFolder) # create folder if it does not exist (for the first image to save basicly) 
				 
				outPath = os.path.join(outFolder,well+'.tif') 
				IJ.save(Projected,outPath)