'''
'''
import pprint
import collections
import copy
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import os
#from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.realpath(__file__))
DATA_FILES = os.path.join(HERE, 'Experimental Mice Data')

def habdata(DATA_FILES):
    for fileName in os.listdir(DATA_FILES): #parses all the data files in each folder in DATA_FILES
        DATA_FILES = os.path.join(HERE, 'Experimental Mice Data', fileName)
        for fileName in os.listdir(DATA_FILES):
            full_path = os.path.join(DATA_FILES, fileName)
            with open(full_path) as f:
                timeDict = collections.OrderedDict()
                finalDict = collections.OrderedDict()
                visitNumber=0
                valves = ['BOT LEFT', 'BOT RIGHT', 'TOP LEFT', 'TOP RIGHT']                
                
                for valve in valves: # create valve keys inside dict
                    timeDict[valve] = collections.OrderedDict()
                    finalDict[valve] = collections.OrderedDict()
                
                for line in f: #put valve visited and enter and exit times into timeDict
                    if 'Strawberry Valve' in line: #stop loop when 'Strawberry Valve' is found and put its location in the dict
                        svalveSplit = line.split(':')
                        svalveLocation = (svalveSplit[1])
                        svalveLocation = svalveLocation.rstrip()
                        timeDict['SBVALVE'] = svalveLocation
                        break
                    lineSplit = line.split('|')
                    enteredTime = lineSplit[1].split(':')
                    exitTime = lineSplit[2].split(':')
                    timeDict[visitNumber]={}
                    timeDict[visitNumber][lineSplit[0]] = (enteredTime[1], exitTime[1])
                    visitNumber+=1
                       
                        
                for valve in valves:#put the times into their respective valve dictionaries
                    for number in range(visitNumber):
                        for k,v in timeDict[number].items():
                            if k == valve:#
                                timeDict[valve][number] = v
                                if number > visitNumber-2:
                                    break   
                                
#                for valve in valves: '''unsure'''
                                
                    #first half of combining consecutive data (<200ms between consecutive investigations)
                    visitList = [] #visitation number
                    for k,v in timeDict[valve].items():
                        visitList.append(k)
                        
                    for index in range(len(visitList)): #visitList = [0,1,2,5,13] index = [0,1,2,3,4]
                        if index+1 < len(visitList):#make sures to not go over list length
                            if (visitList[index+1] - visitList[index]) == 1: #checks consecutive visits
                                enter1, exit1 = timeDict[valve][visitList[index]]
                                enter2, exit2 = timeDict[valve][visitList[index+1]]
                                if (float(enter2) - float(exit1))*1000 < 200:
                                    timeDict[valve][visitList[index+1]] = (enter1, exit2) #replaces the dict with new data
                                    continue
                                
                copyDict = copy.deepcopy(timeDict)
                for valve in valves:#final half of combining consecutive data
                    visitList = [] #visitation number, need to make new list because timeDict was updated
                    for k,v in timeDict[valve].items():
                        visitList.append(k)
                        
                    for index in range(len(visitList)): #visitList = [0,1,2,5,13] index = [0,1,2,3,4]
                        if index+1 < len(visitList):
                            enter1, exit1 = timeDict[valve][visitList[index]]
                            enter2, exit2 = timeDict[valve][visitList[index+1]]
                            if enter1 == enter2:
                                del copyDict[valve][visitList[index]]
                                
                finalDict = copy.deepcopy(copyDict)
                for valve in valves:
                #since we have combined consecutive data, (<200ms between consecutive investigations)
                #we can now delete investigations that are <200 ms
                    visitList = [] #visitation number
                    for k,v in copyDict[valve].items():
                        visitList.append(k)
                        
                    for index in range(len(visitList)): #visitList = [0,1,2,5,13] index = [0,1,2,3,4]
                        enter1, exit1 = copyDict[valve][visitList[index]]
                        if (float(exit1) - float(enter1))*1000 < 200:
                            del finalDict[valve][visitList[index]]
                
                for line in f: #gets the total trial time
                    line = line.rstrip()
                    if 'Total time was' in line:
                        splitLines = line.split(',')
                        combine = ('time', svalveLocation)
                        combined = ''.join(combine)
                        this = str(splitLines[0])
                        remove = "('"
                        for char in remove:
                            this = this.replace(char,"")
                            
                        
                        combined = combined.rstrip() #do this so that \n doesn't mess up 'if combined == this'
                        this = this.rstrip()
                        finalDict['TOTAL TIME'] = (float(splitLines[1].lstrip()))
                
                '''
                make graph
                '''
                y_pos = np.arange(4)
                totalTime = (finalDict['TOTAL TIME'], finalDict['TOTAL TIME'], finalDict['TOTAL TIME'], finalDict['TOTAL TIME']) #total width of the bars for each of the 4 valves
                fig = plt.figure(figsize=(17,14))
                ax = fig.add_subplot(111)
                ax.barh(y_pos, totalTime,color='y',align='center')
                
                n=0
                for valve in valves: #visitList = [0,1,2,5,13] index = [0,1,2,3,4]
                    visitList = []
                    for k,v in finalDict[valve].items():
                        visitList.append(k)

                    for index in range(len(visitList)):
                        enter1, exit1 = finalDict[valve][visitList[(index+1)*-1]]
                        width1 = round(float(exit1)) #have to round numbers up/down so that it works with graphing
                        blank1 = round(float(enter1))
                        investigation = ax.barh(n, width1,color='b',align='center')
                        roaming = ax.barh(n, blank1,color='y',align='center')
                    n+=1
                
                firstLegend = ax.legend((investigation,roaming), ('Investigation','Roaming'))
                plt.gca().add_artist(firstLegend)                
                
                #puts the valve and their respective visitations onto the 2nd legend
                botLeft = ('BOT LEFT=', str(len(finalDict['BOT LEFT'])))
                botLeft = ''.join(botLeft)
                botRight = ('BOT RIGHT=', str(len(finalDict['BOT RIGHT'])))
                botRight = ''.join(botRight)
                topLeft = ('TOP LEFT=', str(len(finalDict['TOP LEFT'])))
                topLeft = ''.join(topLeft)
                topRight = ('TOP RIGHT=', str(len(finalDict['TOP RIGHT'])))
                topRight = ''.join(topRight)
                
                title2 = ('Investigations\n', topRight, topLeft, botRight, botLeft)
                title2 = "\n".join(title2)
                
                
                secondLegend=ax.legend(['',], ('',), loc=4, title=title2)
                secondLegend.get_title().set_fontsize('13')
               
                for index in range(len(valves)): # puts stars on the strawberry valve
                    if finalDict['SBVALVE'] in valves[index]:
                        combine = ('***', valves[index])
                        valves[index] = ''.join(combine)
                        
                        
                        
                ax.set_yticks(y_pos)
                ax.set_yticklabels(valves)
                ax.set_ylabel('Valves')
                ax.set_xticks(np.arange(0,finalDict['TOTAL TIME']+350,200)) #expand a lil so that there is room for the legend
                ax.set_xlabel('Time')
                ax.set_title(fileName) # make it so graph title is the mouse file name
                
                #saves pic into the folder that the data came from
                splitFileName = fileName.split('.')
                newFileLocation = os.path.join(DATA_FILES, str(splitFileName[0]) + 'analyzed' + '.png')
                pprint.pprint (finalDict)
                plt.savefig(newFileLocation)
#                plt.show()
                plt.close()

habdata(DATA_FILES)
