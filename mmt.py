'''
Adapted and modified from Adrian Rosebrock’s basic motion detection and tracking program

 USAGE WinPython command prompt
 python mmd.py
 python mmd.py --video videos/example_01.avi
 python mmd.py -v output.avi
line 225: replace vtime with the time you want in between valves (random for now)

'''
import argparse
import datetime
import time
import cv2
import numpy as np
import threading
import thread
import serial
import random
import math


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
timestr = time.strftime("%Y%m%d-%H%M%S")
f = open(timestr + '.txt', 'w')
#f=file('mmd4.txt','w')
img = None
xgreater = False
xless = False
ygreater = False
yless = False
box=np.zeros(shape=(4,2))
box2=np.zeros(shape=(4,2))
radius=10
textColor=(0,0,255) #red
textColor2=(0,255,0) #green
textColor3=(255,0,0)# dark blue
circleColor=(0,255,0) #green
circleColor2=(255,0,0) #dark blue
circleColor3=(0,0,255) #red
circleColor4=(255,255,150) #light cucumber

#this list will contain the coords for the center of the mouse in each frame. this allows you to compare center cords, recent vs present
#the initial values act as initializers
centerList=[(0,1),(2,3),(4,5),(5,6),(7,8)]
centerList2=[]
headCoord=[(0,1), (1,2), (0,0)]

#circle center coordinates and radius of the 5 odor valves
#circleDict= {'topLeft':{'x': 0, 'y': 0, 'r': 0}, 'topRight':{'x': 0, 'y': 0, 'r': 0},'botLeft':{'x': 0, 'y': 0, 'r': 0},
#             'botRight':{'x': 0, 'y': 0, 'r': 0}, 'middle':{'x': 0, 'y': 0, 'r': 0}}

topLeft = False
topRight = False
botLeft = False
botRight = False
midCenter = False

timeTopLeft = 0
timeTopRight = 0
timeBotLeft = 0
timeBotRight = 0
timeMidCenter = 0

topLeftStart = 0
botLeftStart = 0
botRightStart = 0
topRightStart = 0
midCenterStart = 0
start = time.time()
endTime = 520 #seconds
zoneTime = 60 #how long the mouse stays at valve until forced valve sswtich
stopValve = False

randomValve = None
inZone = False
inZoneTime = 0

valve9ON = False
valve10ON = False
valve11ON = False
valve12ON = False
randomValve = None

#arduino = serial.Serial('COM3', 9600)

def findCenter(contours):
    global center, radius
    (x,y),radius = cv2.minEnclosingCircle(contours)
    center = (int(x),int(y))
    radius = int(radius)

def highestLowestXY(list):
    global coord12, coord12str, coord34, coord34str, coord56, coord56str, coord78, coord78str, sortedCoordList , sortedCoordList2
    sortedCoordList=sorted(list) #sort by x values
    sortedCoordList2=sorted(list, key=lambda x: (x[0][1], x[0][0])) #sort by y values
    
    value1=sortedCoordList[0][0][0] #first, lowest x value
    value2=sortedCoordList[0][0][1] ##y value to the lowest x value
    coord12=(value1,value2)
    coord12str=str(coord12)
    value3=sortedCoordList[-1][0][0] #highest x value
    value4=sortedCoordList[-1][0][1] #y value to the highest x value
    coord34=(value3,value4)
    coord34str=str(coord34)
    
    value5=sortedCoordList2[0][0][0] #x value for the lowest y value
    value6=sortedCoordList2[0][0][1] #frst, lowest y value
    coord56=(value5,value6)
    coord56str=str(coord56)        
    value7=sortedCoordList2[-1][0][0] #x value for the highest y value
    value8=sortedCoordList2[-1][0][1] #highest y value
    coord78=(value7,value8)
    coord78str=str(coord78)

def boundingrekt(contours):
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    comma=','
    jointhis=(str(x),str(y))
    comma.join(jointhis)
    cv2.putText(frame , comma.join(jointhis), (x,y),cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,255)) 
    
def drawcoord(frame, coord,radius, circleColor, textColor):
    cv2.circle(frame, coord, radius/20, circleColor, 2)
    cv2.putText(frame , str(coord), coord,cv2.FONT_HERSHEY_SIMPLEX, .5, textColor)

def sendString(arduinoString):
    global valve9ON, valve10ON, valve11ON, valve12ON
    time.sleep(1)
    arduino.write(arduinoString)
    if arduinoString == '9off':
        print '9off'
        valve9ON = False
        valve9off.cancel()
    if arduinoString == '10off':
        print '10off'
        valve10ON = False
        valve10off.cancel()
    if arduinoString == '11off':
        print '11off'
        valve11ON = False
        valve11off.cancel()
    if arduinoString == '12off':
        print '12off'
        valve12ON = False
        valve12off.cancel()
#    valve9ON = False
#    valve10ON = False
#    valve11ON = False
#    valve12ON = False
#    print valve9ON, 'valve9ON'
#    print valve10ON, 'valve10ON'
#    print valve11ON, 'valve11ON'
#    print valve12ON, 'valve12ON'
        
        
def controlvalve(vtime): # run this the whole time. vtime = time that a valve is on
    global valve9ON, valve10ON, valve11ON, valve12ON, randomValve, valve9off, valve10off, valve11off, valve12off    
    vtime = 6    
    time.sleep(3)
    while True and stopValve == False:
#        print 'controlvalve ON'
        if valve9ON == False and valve10ON == False and valve11ON == False and valve12ON == False:
            print 'finding random valve'
            valveList = [9,10,11,12]
            numberPicked = False
            if randomValve == None: #first iteration, choose a random valve number between 9 and 13
#                randomValve = (randrange(9,11))
                randomValve = random.choice(valveList)
                numberPicked = True
                
            for valveNumber in valveList: #makes it so that the program doesn't pick the same valve twice
                if numberPicked == False:
                    if randomValve == valveNumber:
                        valveList.remove(valveNumber)
                        randomValve = random.choice(valveList)
                        numberPicked = True
                
                #see what number is picked, and then turn on that valve corresponding to that number
            if randomValve == 9:
                time.sleep(1)
                arduino.write('9on')
                print '9on'
                valve9ON = True
                valve9off = threading.Timer(interval = vtime, function = sendString, args = ['9off'])
                valve9off.start() #after vtime seconds, valve9 will turn off
            if randomValve == 10:
                time.sleep(1)
                arduino.write('10on')
                print '10on'
                valve10ON = True
                valve10off = threading.Timer(interval = vtime, function = sendString, args = ['10off'])
                valve10off.start() #after vtime seconds, valve10 will turn off
            if randomValve == 11:
                time.sleep(1)
                arduino.write('11on')
                print '11on'
                valve11ON = True
                valve11off = threading.Timer(interval = vtime, function = sendString, args = ['11off'])
                valve11off.start() #after vtime seconds, valve11 will turn off
            if randomValve == 12:
                time.sleep(1)
                arduino.write('12on')
                print '12on'
                valve12ON = True
                valve12off = threading.Timer(interval = vtime, function = sendString, args = ['12off'])
                valve12off.start() #after vtime seconds, valve12 will turn off
#            print valve9ON, 'valve9ON'
#            print valve10ON, 'valve10ON'
#            print valve11ON, 'valve11ON'
#            print valve12ON, 'valve12ON'

#thread.start_new_thread(controlvalve, (6,))
#thread.start_new_thread(controlvalve, (vtime,))

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])
    time.sleep(0.25)
# initialize the first frame in the video stream
firstFrame = None
#f.write(datetime.datetime.now())
#f.write('\n')
# loop over the frames of the video
n=1


#arduino = serial.Serial('COM3', 9600)


#threading.Thread(target = controlvalve(vtime)).start()


while True:
    # looks for data input from arduino and then prints it
    # example:arduino tells python that it turned on/off a valve
#    data = arduino.readline()[:-2]
#    if data:
#        print data
    
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break
    
    # filters out blue color from the LEDs
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    lower_blue = np.array([90, 0, 20])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    
    # convert frame to grayscale, and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    gray = cv2.bitwise_not(gray, gray, mask = blue_mask)
    
#    print type(gray)
    gray = cv2.GaussianBlur(gray, (23, 23), 0)
    
    cv2.imshow('TESTY TEST', gray)

    # convert frame to grayscale, and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it, and find where the valves are 
    # puts those coords into a dict so they can be drawn
    if firstFrame is None:
        firstFrame = gray
        cv2.imwrite('firstFrame.jpg',frame)
#        time.sleep(2)
        img = cv2.imread('firstFrame.jpg',0)
        centerList2=[]
        circleDict= {'topLeft':{'x': 0, 'y': 0, 'r': 0}, 'topRight':{'x': 0, 'y': 0, 'r': 0},'botLeft':{'x': 0, 'y': 0, 'r': 0},
                     'botRight':{'x': 0, 'y': 0, 'r': 0}, 'middle':{'x': 0, 'y': 0, 'r': 0}}

#        img = cv2.imread(firstFrame,0)
        img = cv2.medianBlur(img,5)
        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        
#        circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,20,
#                                    param1=50,param2=30,minRadius=0,maxRadius=0)
#        
#        circles = np.uint16(np.around(circles))
#        for i in circles[0,:]:
##             draw the outer circle
#            cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
#        
#        #make center and radius list in centerList2
#        for i in circles[0,:]:
#            xvalue = i[0]
#            yvalue = i[1]
#            radiusOfficial = i[2]+30
#            centerXY=(xvalue,yvalue,radiusOfficial)
#            centerXYstr=str(centerXY)
#            centerList2.append(centerXY)
        #sort centerList2 by sum so that I can find out top left and bottom right valve
        centerList2 = sorted(centerList2, key=sum)
        circleDict['topLeft']['x'] = centerList2[0][0]
        circleDict['topLeft']['y'] = centerList2[0][1]
        circleDict['topLeft']['r'] = centerList2[0][2]
        circleDict['botRight']['x'] = centerList2[-1][0]
        circleDict['botRight']['y'] = centerList2[-1][1]
        circleDict['botRight']['r'] = centerList2[-1][2]
        
        #delete the lowest and highest index's so that we are now left with the unknown valves
#        print centerList2
#        del centerList2[0]
#        print centerList2
#        del centerList2[-1]
        
        #sort again to find the cooresponding cooord to the valves
        centerList2= sorted(centerList2)
        #print centerList2
        circleDict['botLeft']['x'] = centerList2[0][0]
        circleDict['botLeft']['y'] = centerList2[0][1]
        circleDict['botLeft']['r'] = centerList2[0][2]
#        circleDict['middle']['x'] = centerList2[1][0]
#        circleDict['middle']['y'] = centerList2[1][1]
#        circleDict['middle']['r'] = centerList2[1][2]
        circleDict['topRight']['x'] = centerList2[2][0]
        circleDict['topRight']['y'] = centerList2[2][1]
        circleDict['topRight']['r'] = centerList2[2][2]
        
        #print circleDict
        
        
        
        
        #cv2.imshow('detected circles',cimg)
        cv2.imwrite('low3.17.16.drawn.jpg',cimg)
        continue

    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 12, 255, cv2.THRESH_BINARY)[1] #low threshold
    thresh2 = cv2.threshold(frameDelta, 40, 255, cv2.THRESH_BINARY)[1] #higher theshold
    difference = cv2.absdiff(thresh2,thresh)
#    cv2.imwrite('firstframe324242.jpg', firstFrame)
#    frame2 = (frame)
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=1)
    thresh2 = cv2.dilate(thresh2, None, iterations=1)
#    print cv2.absdiff(thresh2,thresh)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    (cnts2, _) = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  

    # loop over the contours, low threshold
    for c in cnts:
#        # if the contour is too small, ignore it
##        if cv2.contourArea(c) > 5000:
##            continue
        clist=c.tolist()
        highestLowestXY(clist)
#        
        findCenter(c)
        
        rect = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(rect)
#        print type(box)
        box = np.int0(box)
#        print box
#        im = cv2.drawContours(frame,[box],0,(0,0,255),2)        
#        for x,y in box:
#            drawcoord(frame,(x,y),radius,circleColor, textColor)

    #high threshold
    for c2 in cnts2:
        #convert c, which is an array, to a list
        clist=c2.tolist()
        highestLowestXY(clist)
        
        findCenter(c2)

#        drawcoord(frame,headCoord[-1],radius,circleColor, textColor)
        centerList.append(center)
        rect2 = cv2.minAreaRect(c2)
        box2 = cv2.cv.BoxPoints(rect2)
        box2 = np.int0(box2)

#        im = cv2.drawContours(frame,[box2],0,circleColor4,2)  
#        for x,y in box2:
#            drawcoord(frame,(x,y),radius,circleColor2, textColor2)

    sortedbox = np.sort(box,1)        
    sortedbox2 = np.sort(box2)
    boxDifference = box-box2
#    print 'loop'
#    print boxDifference
    sumOfBox = sum(boxDifference)
#    print sumOfBox
    
    #if x value is greater than y value
    if abs(sumOfBox[0]) > abs(sumOfBox[1]): #want x value
        if sumOfBox[0] > 0: #if change in x is greater than 0
            coord1 = (sortedCoordList[0][0][0],sortedCoordList[0][0][1])
            headCoord.append(coord1) #append the smallest x contour
#            print sortedCoordList[0]
        else:
            coord2 = (sortedCoordList[-1][0][0],sortedCoordList[-1][0][1])
            headCoord.append(coord2) #append the highest x contour
    #if x value is less than y value
    if abs(sumOfBox[0]) < abs(sumOfBox[1]): #want y value
        if sumOfBox[1] > 0:
            coord3 = (sortedCoordList2[0][0][0],sortedCoordList2[0][0][1])
            headCoord.append(coord3)
        else:
            coord4 = (sortedCoordList2[-1][0][0],sortedCoordList2[-1][0][1])
            headCoord.append(coord4)
    if headCoord[-1] == (515,417):
        continue
    if headCoord[-1] == (515,418):
        continue
    drawcoord(frame,headCoord[-1],radius, circleColor, textColor)
#    print headCoord[-1], '|', datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    
#    for item in range(len(valveCenter)):
#        centerx = (int(valveCenter[item][0]), int(valveCenter[item][1]))
#        radiusx = int(valveRadius[item])
#        if (headCoord[-1][0] - int(valveCenter[item][0]))**2 + (headCoord[-1][1] - int(valveCenter[item][1]))**2 <= int(valveRadius[item])**2:
#            print 'yes'
#        else:
#            print 'no'
    
        #draw outline of odor valves (5 of them)
    for k,v in circleDict.iteritems():
        
        cv2.circle(frame, (v['x'],v['y']), v['r'], (0,255,0),2)
        
    if topLeft == True:
        if (headCoord[-1][0] - circleDict['topLeft']['x'])**2 + (headCoord[-1][1] - circleDict['topLeft']['y'])**2 <= circleDict['topLeft']['r']**2:
#            print 'TOP LEFT'        
            cv2.circle(frame, (circleDict['topLeft']['x'], circleDict['topLeft']['y']), circleDict['topLeft']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > zoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendString('9off')
        else:
            topLeft = False
            topLeftEnd = time.time()
            
            timeEntered = round(topLeftStart - start, 2)
            enteredStr = ('Entered', str(timeEntered))
            enteredStrJoined = (':').join(enteredStr)
            
            timeExited = round(topLeftEnd - start, 2)
            exitedStr = ('Exited', str(timeExited))
            exitedStrJoined = (':').join(exitedStr)
            
            timeTotal = round(topLeftEnd - topLeftStart, 2)
            timeTotalStr = ('Total', str(timeTotal))
            timeTotalStrJoined = (':').join(timeTotalStr)
            
            topLeftStr = ('TOP LEFT', enteredStrJoined, exitedStrJoined, timeTotalStrJoined)
            topLeftStrJoined = ('|').join(topLeftStr)
            f.write(str(topLeftStrJoined))            
            f.write('\n')
            print topLeftStrJoined
            timeTopLeft += topLeftEnd - topLeftStart
            inZoneTime = 0
        
        
        
    #top left
    if (headCoord[-1][0] - circleDict['topLeft']['x'])**2 + (headCoord[-1][1] - circleDict['topLeft']['y'])**2 <= circleDict['topLeft']['r']**2 and topLeft == False:
#        print 'TOP LEFT'
        cv2.circle(frame, (circleDict['topLeft']['x'], circleDict['topLeft']['y']), circleDict['topLeft']['r'], (0,0,255),2)
        topLeft = True
        topLeftStart = time.time()
#        inZone = True
        inZoneTime = time.time()
        
        
    if botRight == True:
        if (headCoord[-1][0] - circleDict['botRight']['x'])**2 + (headCoord[-1][1] - circleDict['botRight']['y'])**2 <= circleDict['botRight']['r']**2:
            cv2.circle(frame, (circleDict['botRight']['x'], circleDict['botRight']['y']), circleDict['botRight']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > zoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendString('11off')
        else:
            botRight = False
            botRightEnd = time.time()
            
            timeEntered = round(botRightStart - start, 2)
            enteredStr = ('Entered', str(timeEntered))
            enteredStrJoined = (':').join(enteredStr)
            
            timeExited = round(botRightEnd - start, 2)
            exitedStr = ('Exited', str(timeExited))
            exitedStrJoined = (':').join(exitedStr)
            
            timeTotal = round(botRightEnd - botRightStart, 2)
            timeTotalStr = ('Total', str(timeTotal))
            timeTotalStrJoined = (':').join(timeTotalStr)
            
            botRightStr = ('BOT RIGHT', enteredStrJoined, exitedStrJoined, timeTotalStrJoined)
            botRightStrJoined = ('|').join(botRightStr)    
            f.write(str(botRightStrJoined))
            f.write('\n')
            print botRightStrJoined
            timeBotRight += botRightEnd - botRightStart
            inZoneTime = 0
            
    #bottom right
    if (headCoord[-1][0] - circleDict['botRight']['x'])**2 + (headCoord[-1][1] - circleDict['botRight']['y'])**2 <= circleDict['botRight']['r']**2 and botRight == False:
#        print 'BOT RIGHT'        
#        f.write('BOT RIGHT\n')    
        cv2.circle(frame, (circleDict['botRight']['x'], circleDict['botRight']['y']), circleDict['botRight']['r'], (0,0,255),2)
        botRight = True
        botRightStart = time.time()
        inZoneTime = time.time()
        
        
    if botLeft == True:
        if (headCoord[-1][0] - circleDict['botLeft']['x'])**2 + (headCoord[-1][1] - circleDict['botLeft']['y'])**2 <= circleDict['botLeft']['r']**2:
            cv2.circle(frame, (circleDict['botLeft']['x'], circleDict['botLeft']['y']), circleDict['botLeft']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > zoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendString('10off')
        else:
            botLeft = False
            botLeftEnd = time.time()
            
            timeEntered = round(botLeftStart - start, 2)
            enteredStr = ('Entered', str(timeEntered))
            enteredStrJoined = (':').join(enteredStr)
            
            timeExited = round(botLeftEnd - start, 2)
            exitedStr = ('Exited', str(timeExited))
            exitedStrJoined = (':').join(exitedStr)
            
            timeTotal = round(botLeftEnd - botLeftStart, 2)
            timeTotalStr = ('Total', str(timeTotal))
            timeTotalStrJoined = (':').join(timeTotalStr)
            
            botLeftStr = ('BOT LEFT', enteredStrJoined, exitedStrJoined, timeTotalStrJoined)
            botLeftStrJoined = ('|').join(botLeftStr)    
            f.write(str(botLeftStrJoined))
            f.write('\n')            
            print botLeftStrJoined
            timeBotLeft += botLeftEnd - botLeftStart
            inZoneTime = 0
            
    #bottom left
    if (headCoord[-1][0] - circleDict['botLeft']['x'])**2 + (headCoord[-1][1] - circleDict['botLeft']['y'])**2 <= circleDict['botLeft']['r']**2 and botLeft == False:
#        print 'BOT LEFT'        
#        f.write('BOT LEFT\n')  
        cv2.circle(frame, (circleDict['botLeft']['x'], circleDict['botLeft']['y']), circleDict['botLeft']['r'], (0,0,255),2)
        botLeft = True
        botLeftStart = time.time()
        inZoneTime = time.time()
        
    if topRight == True:
        if (headCoord[-1][0] - circleDict['topRight']['x'])**2 + (headCoord[-1][1] - circleDict['topRight']['y'])**2 <= circleDict['topRight']['r']**2:
            cv2.circle(frame, (circleDict['topRight']['x'], circleDict['topRight']['y']), circleDict['topRight']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > zoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendString('12off')
        else:
            topRight = False
            topRightEnd = time.time()
            
            timeEntered = round(topRightStart - start, 2)
            enteredStr = ('Entered', str(timeEntered))
            enteredStrJoined = (':').join(enteredStr)
            
            timeExited = round(topRightEnd - start, 2)
            exitedStr = ('Exited', str(timeExited))
            exitedStrJoined = (':').join(exitedStr)
            
            timeTotal = round(topRightEnd - topRightStart, 2)
            timeTotalStr = ('Total', str(timeTotal))
            timeTotalStrJoined = (':').join(timeTotalStr)
            
            topRightStr = ('TOP Right', enteredStrJoined, exitedStrJoined, timeTotalStrJoined)
            topRightStrJoined = ('|').join(topRightStr)
            f.write(str(topRightStrJoined))            
            f.write('\n')
            print topRightStrJoined
            timeTopRight += topRightEnd - topRightStart
            inZoneTime = 0
            
    #top right
    if (headCoord[-1][0] - circleDict['topRight']['x'])**2 + (headCoord[-1][1] - circleDict['topRight']['y'])**2 <= circleDict['topRight']['r']**2 and topRight == False:
#        print 'TOP RIGHT'        
#        f.write('TOP RIGHT\n')
        cv2.circle(frame, (circleDict['topRight']['x'], circleDict['topRight']['y']), circleDict['topRight']['r'], (0,0,255),2)
        topRight = True
        topRightStart = time.time()
        inZoneTime = time.time()
        
#    if midCenter == True:
#        if (headCoord[-1][0] - circleDict['middle']['x'])**2 + (headCoord[-1][1] - circleDict['middle']['y'])**2 <= circleDict['middle']['r']**2:
#            cv2.circle(frame, (circleDict['middle']['x'], circleDict['middle']['y']), circleDict['middle']['r'], (0,0,255),2)
#            inZoneTime += time.time() - inZoneTime
#            if inZoneTime > zoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
#                sendString('13off')
#        else:
#            midCenter = False
#            midCenterEnd = time.time()
#            timeMidCenter += midCenterEnd - midCenterStart
#            inZoneTime = 0
#    #center
#    if (headCoord[-1][0] - circleDict['middle']['x'])**2 + (headCoord[-1][1] - circleDict['middle']['y'])**2 <= circleDict['middle']['r']**2 and midCenter == False:
#        cv2.circle(frame, (circleDict['middle']['x'], circleDict['middle']['y']), circleDict['middle']['r'], (0,0,255),2)
#        midCenter = True
#        midCenterStart = time.time()
#        inZoneTime = time.time()        
        
#    f.write(str(headCoord[-1]))
#    f.write('|')
#    f.write(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
#    f.write('\n')
            
    # draw the text and timestamp on the frame
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 226), 1)
        

    
    
    # draws mouse contours
#    cv2.drawContours(frame, cnts2, -1, (255,255,0), 3)
    cv2.imshow("Main", frame)
#    cv2.imshow("Mai2n", frameDelta)
#    cv2.imshow("Thresh2", thresh2)
    cv2.imshow("Thresh", thresh)
#    cv2.imshow("Thresh2", thresh2)
#    cv2.imshow("Frame Delta", frameDelta)
#    cv2.imwrite('low.jpg', frame)
#    cv2.imwrite('high.jpg', frameDelta)
#    cv2.imshow("difference", difference)









    # if the `esc` key is pressed, break from the loop
    #also breaks when program exceeds 'endtime' amount of time
    key = cv2.waitKey(7) % 0x100
#    if key == 27 or key == 10 or (time.time() - start) > endTime:
        #if the mouse is still at the valve when the time ends or esc is pressed
    if key == 27 or key == 10:
        time.sleep(1)        
        if valve9ON == True:
            sendString('9off')
        if valve10ON == True:
            sendString('10off')
        if valve11ON == True:
            sendString('11off')
        if valve12ON == True:
            sendString('12off')
#        if valve13ON == True:
#            sendString('13off')
        if topLeft == True:
#            time.sleep(1)
            topLeft = False
            topLeftEnd = time.time()
            timeTopLeft += topLeftEnd - topLeftStart
#            print '9offFINAL'
#            sendString('9off')
        if botRight == True:
            botRight = False
            botRightEnd = time.time()
            timeBotRight += botRightEnd - botRightStart
#            print '11offFINAL'
#            sendString('11off')
            
        if botLeft == True:
            botLeft = False
            botLeftEnd = time.time()
            timeBotLeft += botLeftEnd - botLeftStart
#            print '10offFINAL'
#            sendString('10off')
        if topRight == True:
            topRight = False
            topRightEnd = time.time()
            timeTopRight += topRightEnd - topRightStart
#            print '12offFINAL'
#            sendString('12off')
            
        if midCenter == True:
            midCenter = False
            midCenterEnd = time.time()
            timeMidCenter += midCenterEnd - midCenterStart    
#            sendString('13off')                     
            
        stopValve = True
        print start
        end = time.time()
        print end
        totalTime = ('Total time was ', end - start, 'seconds')
#        print(end - start), 'seconds'
        print totalTime
        f.write(str(totalTime))
        f.write('\n')
#        f.write(str(headCoord[-1]))
#        f.write('\n')
        
        print 'timeTopLeft', timeTopLeft
        topLeft = ('timeTopLeft', timeTopLeft, 'seconds')
        f.write(str(topLeft))
        f.write('\n')
        print 'timeTopRight', timeTopRight
        topRight = ('timeTopRight', timeTopRight, 'seconds')
        f.write(str(topRight))
        f.write('\n')
        print 'timeBotLeft', timeBotLeft
        botLeft = ('timeBotLeft', timeBotLeft, 'seconds')
        f.write(str(botLeft))
        f.write('\n')
        print 'timeBotRight', timeBotRight
        botRight = ('timeBotRight', timeBotRight, 'seconds')
        f.write(str(botRight))
        f.write('\n')
#        print 'timeMidCenter', timeMidCenter
#        print circleDict
        cv2.imwrite('low.jpg', frame)
        cv2.imwrite('high.jpg', frameDelta)
        f.close()
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
