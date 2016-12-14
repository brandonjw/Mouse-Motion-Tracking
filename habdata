# -*- coding: utf-8 -*-
"""
time at strawberry valve

time in box roaming (total time - total valve time)

time at blank valve (total valve time - strawberry valve time)
"""
import os

HERE = os.path.dirname(os.path.realpath(__file__))
DATA_FILES = os.path.join(HERE, 'Experimental Mice Data', '12042016 Data BW')
#svalveLocation = None
#svalveFound = False
#def analtime(valve):
#    if valve == this:
        

def habdata(file_loc):
#    global svalveLocation
    resultList = ['Total time was', 'timetopLeft', 'timetopRight', 'timebotLeft', 'timebotRight']
#    resultDict = {'Total time was', 'timetopLeft'}
    resultDict = {}
    svalveLocation = None
    svalveFound = False
    for fileName in os.listdir(file_loc):
        splitFileName = fileName.split('.')
        newFileLocation = os.path.join(DATA_FILES, splitFileName[0] + 'analyzed' + '.txt') #makes it so that it writes the txt file into Experimental Mice Data folder
        newFile = open(newFileLocation, 'w')
#        newFile = open(splitFileName[0] + 'analyzed' + '.txt', 'w')
#        print (newFile)
        full_path = os.path.join(DATA_FILES, fileName)
        with open(full_path) as f:
            for line in f:
                if 'Strawberry Valve' in line:
                    svalveSplit = line.split(':')
                    svalveLocation = (svalveSplit[1])
#                    print (svalveLocation) #example: topRight
                    svalveFound = True
#                    print (line)
                if svalveFound == True:
                    if '(' in line:
#                        print (line)
                        splitLines = line.split(',')
                        combine = ('time', svalveLocation)
                        combined =  ''.join(combine)
#                        print (combined)
                        this = str(splitLines[0])
                        remove = "('"
                        for char in remove:
                            this = this.replace(char,"")
                            
                        
                        combined = combined.rstrip() #do this so that \n doesn't mess up (if combined == this)
                        this = this.rstrip()
#                        print (this)
#                        for                       
                        for valve in resultList:
                            if valve == this:
                                resultDict[valve] = float(splitLines[1].lstrip())
#                                (valve, splitLines[1].lstrip())
#                        print (resultDict)
                        
#                        if 'Total time was' == this:
#                            resultDict['Total time was'] = (splitLines[1].lstrip())
#                            print (resultDict)
                            
                            
                            
#                        timetopLeft = function(timetopLeft)
                        
                        
                        
                        
                        
                        
#                        if 'Total time was' == this:
#                            totalTime = (splitLines[1].lstrip())
##                            print (totalTime)
#                        if 'timetopLeft' == this:
#                            timetopLeft = (splitLines[1].lstrip())
#                            print (timetopLeft)
                            
                        if combined == this: #finds time at strawberry valve
                            sTime =  float((splitLines[1].lstrip()))

                            sTime = round(sTime, 2)

#                            print (sTime)
                            timeAtSvalveStr = ('Time At Strawberry Valve', str(sTime)) #this represents the time at strawberry valve
                            timeAtSvalveStr = '|'.join(timeAtSvalveStr)
#                            print (timeAtSvalveStr)
            totalTime = resultDict['Total time was']
            totalValveTime = resultDict['timetopLeft'] + resultDict['timetopRight'] + resultDict['timebotLeft'] + resultDict['timebotRight']
            totalValveTime = round(totalValveTime, 2)
            
            blankValveTime = totalValveTime - sTime 
            roamTime = totalTime - totalValveTime
            resultDict['roamTime'] = roamTime
            resultDict['Strawberry Valve Time'] = sTime
            resultDict['blankValveTime'] = blankValveTime
            for k,v in resultDict.items():
                info = k,v
#                info = ('|'.join(str(info)))
                newFile.write(str(info))
                newFile.write('\n')
#                print (k,v)
#                            resultDict[]
#                            print (combinedtimeAtSvalve)
                            
#                        ok = this.strip('was')
#                        print (ok)
#                        if combined in str(splitLines[0]):
#                            print (splitLines[0])
                            
#                            print (splitLines[0])
#                    if svalveLocation in line:
#                        print (line)
#                if svalveFound == True and svalveLocation in line:
#                    svalveFound = False
#                    print (line)
                    
#                if svalveLocation in line:
#                    print (line)
                  
        

habdata(DATA_FILES)

