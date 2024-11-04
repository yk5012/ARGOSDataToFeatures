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
arcpy.env.overwriteOutput = True

#%% Set input variables 
inputFolder = arcpy.GetParameterAsText(0) #'V:/ARGOSTracking/Data/ARGOSData'
outputFC = arcpy.GetParameterAsText(1) #"V:/ARGOSTracking/Scratch/ARGOStrack.shp"
# Note we are using forward slashes because they work for paths 
# without incurring the magicness of backward slashes
outputSR = arcpy.GetParameterAsText(2) #arcpy.SpatialReference(54002)


#%% Prepare a new feature class to which we'll add tracking points
# Create an empty feature class; requires the path and name as separate parameters
outPath,outName = os.path.split(outputFC) 
    # os.path.split does exactly what we need - splitting string to path and name
arcpy.CreateFeatureclass_management(outPath,outName,"POINT","","","",outputSR)
    # same thing as arcpy.management.CreateFeatureclass()

#%% 1d. Adding attributes to newly created output
# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.management.AddField(outputFC,"TagID","LONG")
arcpy.management.AddField(outputFC,"LC","TEXT")
arcpy.management.AddField(outputFC,"Date","DATE")


#%%
# Create the insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])
    # when we add a row, can access records in the specified order here
    # creating a cursor places a lock on the schema so you can't overwrite or edit the file
    # this is why we want to delete cursor after done


#%% Interate throuhg all files in the inputFolder 
for inputFile in os.listdir(inputFolder):
    # skip the readme file 
    if inputFile == "README.txt":
        continue

    # Construct a while loop to iterate through all lines in the datafile
    # Open the ARGOS data file for reading
    arcpy.AddMessage(f"Working on file {inputFile}")
    inputFileObj = open(os.path.join(inputFolder, inputFile),'r')
        # inputFile won't work in open() because it's just the name with no path
        # if we use os.path.join, this is what we get for inputFileObj:
        # V:/ARGOSTracking/Data/ARGOSData\\2003DG.txt
        # \\ and / are treated as same thing

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
            obsDate = lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
            
            #Try to convert the coordinates to numbers
            try:

                # Print results to see how we're doing
                print (tagID,"Lat:"+obsLat,"Long:"+obsLon)

                # Convert raw coordinate strings to numbers based on knowledge 
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else: # otherwise it will be south 
                    obsLat = float(obsLat[:-1]) * -1
                if obsLon[-1] == 'E':
                    obsLon = float(obsLon[:-1])
                else: # otherwise it will be west
                    obsLon = float(obsLon[:-1]) * -1

                # Construct a point object from the feature class
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat

                # Convert the point to a point geometry object with spatial reference
                inputSR = arcpy.SpatialReference(4326)
                obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)

                # Create a feature object
                feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") 
                                        + " " + obsTime))
                    # we use obsPointGeom with spatial reference instead of just obsPoint
                    # We are listing records in the order we read the feature class row 
                    # in for the insertcursor, so obsPoint will go in the first space 'Shape@'

            #Handle any error - skips problematic records and moves on
            except Exception as e:
                arcpy.AddWarning(f"Error adding record {tagID} to the output: {e}")
            
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()
        
    #Close the file object
    inputFileObj.close()

# %%
#Delete the cursor object and wrap up
del cur

arcpy.AddMessage("All Done!")

# %%
