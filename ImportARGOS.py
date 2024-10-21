##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2023
## Author: John.Fay@duke.edu (for ENV859)
##---------------------------------------------------------------------

#%% Import modules
import sys, os, arcpy

#%% Set input variables (Hard-wired)
inputFile = 'V:/ARGOSTracking/Data/ARGOSData/1997dg.txt'
outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"
# Note we are using forward slashes because they work for paths 
# without incurring the magicness of backward slashes

# Remember single/double quotes don't matter here as long as consistent within line
#%%
# Construct a while loop to iterate through all lines in the datafile
# Open the ARGOS data file for reading
inputFileObj = open(inputFile,'r')

# Get the first line of data, so we can use a while loop
lineString = inputFileObj.readline()

# Start the while loop 
# We are using while instead of for to conserve memory because we don't know length of file
while lineString:
    
    # Set code to run only if the line contains the string "Date: "
    #if not, skip everything indended under if 
    if ("Date :" in lineString):
        
        # Parse the line into a list
        lineData = lineString.split()
        
        # Extract attributes from the datum header line
        tagID = lineData[0]
        
        # Extract location info from the next line
        line2String = inputFileObj.readline()
        
        # Parse the line into a list
        line2Data = line2String.split()
        
        # Extract the date we need to variables
        obsLat = line2Data[2]
        obsLon= line2Data[5]
        
        # Print results to see how we're doing
        print (tagID,"Lat:"+obsLat,"Long:"+obsLon)
        
    # Move to the next line so the while loop progresses
    lineString = inputFileObj.readline()
    
#Close the file object
inputFileObj.close()
# %%
