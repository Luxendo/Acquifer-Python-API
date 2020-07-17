'''
HYPERSTACK GENERATOR in Fiji 
Read all tif images from an experiment inFolder that contains tif images for the different wells, channel, slices and timepoints 
The script will automatically reads the field from the Filename (using index in the string - FOLLOWING ACQUIFER-IM04 NAMING CONVENTION ex: -A001--...) to generate the well's stack
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
subPos0  = prefs.get("subPos","")
 
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

Win.addMessage("Use specific...")
Win.addStringField("Channel(s) (from 1 to 6) :", Channel0) 
Win.addStringField("Z-slice(s):", Slice0) 
Win.addStringField("Timepoint(s):", Time0) 
Win.addStringField("Sub-position(s):", subPos0) 
Win.addMessage("Note: multiple indexes should be separated by commas")
 
Win.addCheckbox("Show_stack ?", ShowStack0) 
Win.addCheckbox("Save_stack ?", SaveStack0) 
 
Win.addCheckbox("Make_Z-projection ?",doProj0)
Win.addToSameRow()
Win.addChoice("Method",['avg','sd','max','min','sum','median'], ProjMethod0) 
Win.addToSameRow() 
Win.addCheckbox("Show_projection ?",ShowProj0) 
Win.addToSameRow() 
Win.addCheckbox("Save_projection ?",SaveProj0) 
 
 
# Generate tick box with plate layout to select well 
Wells = [] 
for letter in ['A','B','C','D','E','F','G','H']: 
	for column in range(1,13): 
		Wells.append(letter+'%(column)03d' %{"column":column}) # force max 3 digits and leading 0 

BoolWells0 = [True]*96 if not BoolWells0 else BoolWells0 # 1st run peristence is empty hence we initialise with True
Win.addCheckboxGroup(8,12,Wells, BoolWells0)             # Add result from persistence here 
 
Win.addButton('Select all' , ButtonClic() ) # add an instance of our ButtonClic listener class to the button. Button clicked -> event -> call actionPerformed(event) 
Win.addButton('Select none', ButtonClic() ) 

# Add help button, pointing to zenodo
url = "https://doi.org/10.5281/zenodo.3368135"	# Help button should point to the Zenodo page
Win.addHelp(url)

Win.addMessage("This plugin is freely provided by ACQUIFER.")
Win.addMessage("v1.3.0")

# Add doi badge image
doiPath = os.path.join(IJ.getDirectory("ImageJ"), "lib", "BadgeDOI_Hyperstack.png")
DOI=IJ.openImage(doiPath)
Win.addImage(DOI)

Win.showDialog() 
 
 
 
## Recover input 
if (Win.wasOKed()):  
	inFolder	  = Win.getNextString() 
	
	ChoiceChannel = Win.getNextString()  
	ChoiceSlice	  = Win.getNextString() 
	ChoiceTime	  = Win.getNextString() 
	ChoiceSubPos  = Win.getNextString() 
 
	
	ShowStack	 = Win.getNextBoolean()
	SaveStack	 = Win.getNextBoolean()
	
	doProj		 = Win.getNextBoolean()
	ProjMethod 	 = Win.getNextChoice()
	ShowProj	 = Win.getNextBoolean()
	SaveProj 	 = Win.getNextBoolean() 
	
	BoolWells = [Win.getNextBoolean() for i in range( len(Wells) ) ] 
	Selection = {well:choice for well,choice in zip(Wells,BoolWells)} # create a dictionary associating a well to a boolean . Chosen or not 
	#print Selection 
	#print len(Wells) # OK 96 
 
	 
	# Save input into memory/persistence 
	prefs.put("ImageDirectory",inFolder) 
	 
	prefs.put("Channels", ChoiceChannel)  
	prefs.put("Slices", ChoiceSlice) 
	prefs.put("Times", ChoiceTime) 
	prefs.put("subPos", ChoiceSubPos)
 
	prefs.put("ShowStack", ShowStack) 
	prefs.put("SaveStack", SaveStack) 
 	
	prefs.put("doProj", doProj)
	prefs.put("ProjMethod", ProjMethod) 
	prefs.put("ShowProj", ShowProj) 
	prefs.put("SaveProj", SaveProj)
	
	prefs.put(imagej.class, "BoolWells", map(str, BoolWells) ) 	# persitence for list works with string only (hence map str)	 
	# Stop execution if no well selected 
	if BoolWells == [False]*96: 
		IJ.error("No well selected") 
 
	# Reformat input to list after the input has been saved in memory 
	ChoiceChannel = map( int, ChoiceChannel.split(",") ) if ChoiceChannel else []
	ChoiceTime	  = map( int, ChoiceTime.split(",")    ) if ChoiceTime	  else []
	ChoiceSlice   = map( int, ChoiceSlice.split(",")   ) if ChoiceSlice   else []
	ChoiceSubPos  = map( int, ChoiceSubPos.split(",")  ) if ChoiceSubPos  else []
	
	# Find image files for the given channel 
	#inFolder = str(inFolder) # convert Filename object to string object 
	setWell	   = set() # full list of well to know how many iteration for stacking 
	setTime	   = set() 
	setChannel = set() 
	setSlice   = set() 
	setSubPos  = set() 
   
	listMain   = [] # contains tuple with (Filename, Well, TimePoint, Channel, Z-Slice) 
 
	for fname in os.listdir(inFolder): # extract metadata from image Filename  
		if fname.endswith(".tif"): 
 
			# first extract the well field 
			well = fname[1:5] 
 
			# if well is selected in the gui, then extract the other metadata 
			if Selection[well]: # read True/False value from the dict Selection with Well:Choice
 
				try : # int conversion throw an error if the argument string is empty, hence the try  
					subPos   = int(fname[9:11])
					time 	 = int(fname[15:18]) 
					channel  = int(fname[22:23]) 
					sliceIdx = int(fname[27:30])  
				except : 
					IJ.error("Could not get experimental parameters from Filename. Check Filename pattern (IM04 convention)") 
					#raise Exception("Could not get experimental parameters from Filename. Check Filename pattern (IM04 convention)") 
				 
				setWell.add(well) 
 
				 
				## Discover CHANNEL from filename  
				if ChoiceChannel==[]: # No precise channel specified: We add this particular channel to the list 
					setChannel.add(channel) 
					 
				elif channel in ChoiceChannel: # This particular channel was selected
					setChannel.add(channel) 
 
				else: # This particular channel was not selected 
					continue 
 
					 
				 
				## Discover TIME from filename  
				if ChoiceTime==[]: # No precise time specified: We add this particular time to the list
					setTime.add(time) 
					 
				elif time in ChoiceTime: # This particular timepoint was selected
					setTime.add(time) 
 
				else: # This particular timepoint was not selected
					continue 
				 
 
				 
				## Discover Z-SLICE from filename  
				if ChoiceSlice==[]: # No precise slice specified: We add this particular slice to the list
					setSlice.add(sliceIdx) 
					 
				elif sliceIdx in ChoiceSlice: # This particular slice was selected
					setSlice.add(sliceIdx) 
 
				else: # This particular slice was not selected
					continue
					
				
				## Discover SUBPOSITION from filename  
				if ChoiceSubPos==[]: # No precise subPosition specified: We add this particular subPosition to the list
					setSubPos.add(subPos) 
					 
				elif subPos in ChoiceSubPos: # This particular subPosition was selected
					setSubPos.add(subPos) 
 
				else: # This particular subPosition was not selected
					continue
 
				 
				# Append to main list only if it managed to pass the previous if (ie it did not come across a continue statement) 
				listMain.append({"Filename":fname, "well":well, "subPos":subPos, "TimePoint":time, "Channel":channel, "Slice":sliceIdx}) 
 
			 
			else : # the well was not selected in the GUI, go for the next image Filename 
				continue 
 
			 
	if len(listMain) < 1: 
		IJ.error("No image files found in %s satisfying the channel/slice/time selection. Check if extension match and if Filenames match IM04 naming convention" % inFolder) 
		#raise Exception("No image files found in %s satisfying the channel/slice/time selection. Check if extension match and if Filenames match IM04 naming convention" % inFolder) 
 
	# Turn sets into ordered list
	listWell    = sorted(setWell) 
	listSubPos  = sorted(setSubPos)
	listTime    = sorted(setTime)  
	listChannel = sorted(setChannel)  
	listSlice   = sorted(setSlice)  
 
	# Verification 
	print 'Well  : ',        listWell 
	print 'Subpositions : ', listSubPos
	print 'Time  : ',        listTime 
	print 'ChannelIdx  : ',  listChannel 
	print 'Z-Slice : ' ,     listSlice 
 
 
	listMain.sort(key = lambda dico:(dico["well"], dico["subPos"], dico["TimePoint"], dico["Slice"], -dico["Channel"]) ) # sort by Well, SubPositions, Time, Z-slice then Channel (- to have C06 ie BF first) since the hyperstack is created following the default "xyczt" order 
	'''
	for i in listMain : 
		print i 
	'''
	 
	## Loop over wells to do stack and projection 
	for well in listWell: # - TO DO: Add another level in listMain : one per well 
		
		for subPos in listSubPos:
 
			# Gather images for a given well, and put them into a sublist (like a GroupBy)
			IJ.showStatus('Process well : '+well+'...') 
			allSlices = [dico for dico in listMain if (dico["well"]==well and dico["subPos"]==subPos) ] # Sublist containing (fname1,Well, subPos ,Time1,ChannelX,Slice),(fname2,Well, subPos, Time2,ChannelX,Slice)  for one given well ex: only A001  
			#print 'StackSize : ',len(SubList) 
		
			# Get image dimensions of the first image in the list to initialise VStack 
			width, height = dimensionsOf( os.path.join(inFolder, allSlices[0]['Filename']) ) 
			 
			# Initialise Virtual Stack for this well 
			VStack = VirtualStack(width, height, None, inFolder)   
			 
			# Append slices in the VStack 
			for dico in allSlices: 
				Filename = dico["Filename"] 
				VStack.addSlice(Filename) # conversion to ImageProcessor object to append to stack 
		 
				# Once we have finished appending slices, we reconvert back to an ImagePlus object to be able to show and save it 
				ImpName = well + "_subPos" + str(subPos)
				ImpStack = ij.ImagePlus(ImpName, VStack) # well is the title of this hyperstack - Reminder : 1 hyperstack/well 
				#print ImpStack 
				#Stack.show() # Good 
			 
			 
			## Make a hyperstack out of the ImagePlus virtual stack 
			if ImpStack.getStackSize()==1:  
				HyperStack = ImpStack # issue when a single slice in the Hyperstack 
			else: 
				HyperStack = HyperStackConverter.toHyperStack(ImpStack, len(listChannel), len(listSlice), len(listTime),"xyczt","grayscale") # convert PROPERLY ORDERED Stack to Hyperstack  
			 
			 
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