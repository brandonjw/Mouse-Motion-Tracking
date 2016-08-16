'''
 USAGE WinPython command prompt
 python mmd.py
 python mmd.py --video videos/example_01.avi
 python mmd.py -v output.avi
line 225: replace vtime with the time you want in between valves (random for now)

make it so that when esc is pressed tells you how long each valve was on for
'''
#from __future__ import division
import argparse
import datetime
import time
import cv2
import numpy as np
import threading
import thread
import serial
import random

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
f=file('mmd4.txt','w')
#initialize
img = None
xgreater = False
xless = False
ygreater = False
yless = False
box=np.zeros(shape=(4,2))
box2=np.zeros(shape=(4,2))
radius=10
textcolor=(0,0,255) #red
textcolor2=(0,255,0) #green
textcolor3=(255,0,0)# dark blue
circlecolor=(0,255,0) #green
circlecolor2=(255,0,0) #dark blue
circlecolor3=(0,0,255) #red
circlecolor4=(255,255,150) #light cucumber

#this list will contain the coords for the center of the mouse in each frame. this allows you to compare center cords, recent vs present
centerlist=[(0,1),(2,3),(4,5),(5,6),(7,8)]
centerlist2=[]
headcoord=[(0,1), (1,2), (0,0)]

#circle center coordinates and radius of the 5 odor valves
#circleDict= {'topleft':{'x': 0, 'y': 0, 'r': 0}, 'topright':{'x': 0, 'y': 0, 'r': 0},'bottomleft':{'x': 0, 'y': 0, 'r': 0},
#             'bottomright':{'x': 0, 'y': 0, 'r': 0}, 'middle':{'x': 0, 'y': 0, 'r': 0}}

topLeft = False
topRight = False
botLeft = False
botRight = False
midCenter = False

timetopLeft = 0
timetopRight = 0
timebotLeft = 0
timebotRight = 0
timemidCenter = 0

topLeftStart = 0
botLeftStart = 0
botRightStart = 0
topRightStart = 0
midCenterStart = 0
start = time.time()
endTime = 60 #seconds
ZoneTime = 60 #how long the mouse stays at valve until forced valve sswtich
stopvalve = False

randomValve = None
inZone = False
inZoneTime = 0

valve9ON = False
valve10ON = False
valve11ON = False
valve12ON = False
randomValve = None

arduino = serial.Serial('COM3', 9600)

def findcenter(contours):
    global center, radius
    (x,y),radius = cv2.minEnclosingCircle(contours)
    center = (int(x),int(y))
    radius = int(radius)

def highestlowestXY(list):
    global coord12, coord12str, coord34, coord34str, coord56, coord56str, coord78, coord78str, sortedcordlist , sortedcordlist2
    sortedcordlist=sorted(list) #sort by x values
    sortedcordlist2=sorted(list, key=lambda x: (x[0][1], x[0][0])) #sort by y values
    
    value1=sortedcordlist[0][0][0] #first, lowest x value
    value2=sortedcordlist[0][0][1] ##y value to the lowest x value
    coord12=(value1,value2)
    coord12str=str(coord12)
    value3=sortedcordlist[-1][0][0] #highest x value
    value4=sortedcordlist[-1][0][1] #y value to the highest x value
    coord34=(value3,value4)
    coord34str=str(coord34)
    
    value5=sortedcordlist2[0][0][0] #x value for the lowest y value
    value6=sortedcordlist2[0][0][1] #frst, lowest y value
    coord56=(value5,value6)
    coord56str=str(coord56)        
    value7=sortedcordlist2[-1][0][0] #x value for the highest y value
    value8=sortedcordlist2[-1][0][1] #highest y value
    coord78=(value7,value8)
    coord78str=str(coord78)

def boundingrekt(contours):
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    comma=','
    jointhis=(str(x),str(y))
    comma.join(jointhis)
    cv2.putText(frame , comma.join(jointhis), (x,y),cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,255)) 
    
def drawcoord(frame,coord,radius,circlecolor,textcolor):
    cv2.circle(frame,coord,radius/20,circlecolor,2)
    cv2.putText(frame , str(coord), coord,cv2.FONT_HERSHEY_SIMPLEX, .5,textcolor)

def sendstring(arduinostring):
    global valve9ON, valve10ON, valve11ON, valve12ON
    time.sleep(1)
    arduino.write(arduinostring)
    if arduinostring == '9off':
        print '9off'
        valve9ON = False
        valve9off.cancel()
    if arduinostring == '10off':
        print '10off'
        valve10ON = False
        valve10off.cancel()
    if arduinostring == '11off':
        print '11off'
        valve11ON = False
        valve11off.cancel()
    if arduinostring == '12off':
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
    while True and stopvalve == False:
#        print 'controlvalve ON'
        if valve9ON == False and valve10ON == False and valve11ON == False and valve12ON == False:
            print 'finding random valve'
            valveList = [9,10,11,12]
            numberPicked = False
            if randomValve == None: #first iteration, choose a random valve number between 9 and 13
#                randomValve = (randrange(9,11))
                randomValve = random.choice(valveList)
                numberPicked = True
                
            if randomValve == 9 and numberPicked == False: #makes it so that the program doesn't pick the same valve twice
#                randomValve = (randrange(10,11))
                valveList.remove(9)
                randomValve = random.choice(valveList)
                numberPicked = True
            if randomValve == 10 and numberPicked == False:
#                randomValve = (randrange(9,10))
                valveList.remove(10)
                randomValve = random.choice(valveList)
                numberPicked = True
            if randomValve == 11 and numberPicked == False:
#                randomValve = (randrange(9,10))
                valveList.remove(11)
                randomValve = random.choice(valveList)
                numberPicked = True
            if randomValve == 12 and numberPicked == False:
#                randomValve = (randrange(9,10))
                valveList.remove(12)
                randomValve = random.choice(valveList)
                numberPicked = True
                
                #see what number is picked, and then turn on that valve corresponding to that number
            if randomValve == 9:
                time.sleep(1)
                arduino.write('9on')
                print '9on'
                valve9ON = True
                valve9off = threading.Timer(interval = vtime,function = sendstring, args = ['9off'])
                valve9off.start() #after vtime seconds, valve9 will turn off
            if randomValve == 10:
                time.sleep(1)
                arduino.write('10on')
                print '10on'
                valve10ON = True
                valve10off = threading.Timer(interval = vtime,function = sendstring, args = ['10off'])
                valve10off.start() #after vtime seconds, valve10 will turn off
            if randomValve == 11:
                time.sleep(1)
                arduino.write('11on')
                print '11on'
                valve11ON = True
                valve11off = threading.Timer(interval = vtime,function = sendstring, args = ['11off'])
                valve11off.start() #after vtime seconds, valve11 will turn off
            if randomValve == 12:
                time.sleep(1)
                arduino.write('12on')
                print '12on'
                valve12ON = True
                valve12off = threading.Timer(interval = vtime,function = sendstring, args = ['12off'])
                valve12off.start() #after vtime seconds, valve12 will turn off
#            print valve9ON, 'valve9ON'
#            print valve10ON, 'valve10ON'
#            print valve11ON, 'valve11ON'
#            print valve12ON, 'valve12ON'

thread.start_new_thread(controlvalve, (3,))
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
f.write('date')
f.write('\n')
# loop over the frames of the video
n=1


arduino = serial.Serial('COM3', 9600)


threading.Thread(target = controlvalve(vtime)).start()


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
        cv2.imwrite('firstframe.jpg',frame)
#        time.sleep(2)
        img = cv2.imread('firstframe.jpg',0)
        centerlist2=[]
        circleDict= {'topleft':{'x': 0, 'y': 0, 'r': 0}, 'topright':{'x': 0, 'y': 0, 'r': 0},'bottomleft':{'x': 0, 'y': 0, 'r': 0},
                     'bottomright':{'x': 0, 'y': 0, 'r': 0}, 'middle':{'x': 0, 'y': 0, 'r': 0}}

#        img = cv2.imread(firstFrame,0)
        img = cv2.medianBlur(img,5)
        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        
        circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,20,
                                    param1=50,param2=30,minRadius=0,maxRadius=0)
        
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        
        #make center and radius list in centerlist2
        for i in circles[0,:]:
            xvalue = i[0]
            yvalue = i[1]
            radiusOfficial = i[2]+30
            centerXY=(xvalue,yvalue,radiusOfficial)
            centerXYstr=str(centerXY)
            centerlist2.append(centerXY)
        #sort centerlist2 by sum so that I can find out top left and bottom right valve
        centerlist2 = sorted(centerlist2, key=sum)
        circleDict['topleft']['x'] = centerlist2[0][0]
        circleDict['topleft']['y'] = centerlist2[0][1]
        circleDict['topleft']['r'] = centerlist2[0][2]
        circleDict['bottomright']['x'] = centerlist2[-1][0]
        circleDict['bottomright']['y'] = centerlist2[-1][1]
        circleDict['bottomright']['r'] = centerlist2[-1][2]
        
        #delete the lowest and highest index's so that we are now left with the unknown valves
        print centerlist2
        del centerlist2[0]
        print centerlist2
        del centerlist2[-1]
        
        #sort again to find the cooresponding cooord to the valves
        centerlist2= sorted(centerlist2)
        #print centerlist2
        circleDict['bottomleft']['x'] = centerlist2[0][0]
        circleDict['bottomleft']['y'] = centerlist2[0][1]
        circleDict['bottomleft']['r'] = centerlist2[0][2]
        circleDict['middle']['x'] = centerlist2[1][0]
        circleDict['middle']['y'] = centerlist2[1][1]
        circleDict['middle']['r'] = centerlist2[1][2]
        circleDict['topright']['x'] = centerlist2[2][0]
        circleDict['topright']['y'] = centerlist2[2][1]
        circleDict['topright']['r'] = centerlist2[2][2]
        
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
  

    # loop over the contours
#'''low threshold'''
    for c in cnts:
#        # if the contour is too small, ignore it
##        if cv2.contourArea(c) > 5000:
##            continue
        clist=c.tolist()
        highestlowestXY(clist)
#        
        findcenter(c)
        
        rect = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(rect)
#        print type(box)
        box = np.int0(box)
#        print box
#        im = cv2.drawContours(frame,[box],0,(0,0,255),2)        
#        for x,y in box:
#            drawcoord(frame,(x,y),radius,circlecolor, textcolor)

#''' high threshold'''      
    for c2 in cnts2:
        #convert c, which is an array, to a list
        clist=c2.tolist()
        highestlowestXY(clist)
        
        findcenter(c2)

#        drawcoord(frame,headcoord[-1],radius,circlecolor, textcolor)
        centerlist.append(center)
        rect2 = cv2.minAreaRect(c2)
        box2 = cv2.cv.BoxPoints(rect2)
        box2 = np.int0(box2)

#        im = cv2.drawContours(frame,[box2],0,circlecolor4,2)  
#        for x,y in box2:
#            drawcoord(frame,(x,y),radius,circlecolor2, textcolor2)

    sortedbox = np.sort(box,1)        
    sortedbox2 = np.sort(box2)
    boxdifference = box-box2
#    print 'loop'
#    print boxdifference
    sumofbox = sum(boxdifference)
#    print sumofbox
    
    #if x value is greater than y value
    if abs(sumofbox[0]) > abs(sumofbox[1]): #want x value
        if sumofbox[0] > 0: #if change in x is greater than 0
            coord1 = (sortedcordlist[0][0][0],sortedcordlist[0][0][1])
            headcoord.append(coord1) #append the smallest x contour
#            print sortedcordlist[0]
        else:
            coord2 = (sortedcordlist[-1][0][0],sortedcordlist[-1][0][1])
            headcoord.append(coord2) #append the highest x contour
            
    #if x value is less than y value
    if abs(sumofbox[0]) < abs(sumofbox[1]): #want y value
        if sumofbox[1] > 0:
            coord3 = (sortedcordlist2[0][0][0],sortedcordlist2[0][0][1])
            headcoord.append(coord3)
        else:
            coord4 = (sortedcordlist2[-1][0][0],sortedcordlist2[-1][0][1])
            headcoord.append(coord4)
    if headcoord[-1] == (515,417):
        continue
    if headcoord[-1] == (515,418):
        continue
    drawcoord(frame,headcoord[-1],radius,circlecolor, textcolor)
#    print headcoord[-1], '|', datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    
#    for item in range(len(valveCenter)):
#        centerx = (int(valveCenter[item][0]), int(valveCenter[item][1]))
#        radiusx = int(valveRadius[item])
#        if (headcoord[-1][0] - int(valveCenter[item][0]))**2 + (headcoord[-1][1] - int(valveCenter[item][1]))**2 <= int(valveRadius[item])**2:
#            print 'yes'
#        else:
#            print 'no'
    
        #draw outline of odor valves (5 of them)
    for k,v in circleDict.iteritems():
        
        cv2.circle(frame, (v['x'],v['y']), v['r'], (0,255,0),2)
    #if mouse is located at the top left valve
    if topLeft == True:
        if (headcoord[-1][0] - circleDict['topleft']['x'])**2 + (headcoord[-1][1] - circleDict['topleft']['y'])**2 <= circleDict['topleft']['r']**2:
            print 'TOP LEFT'
            cv2.circle(frame, (circleDict['topleft']['x'], circleDict['topleft']['y']), circleDict['topleft']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > ZoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendstring('9off')
        else:
            topLeft = False
            topLeftEnd = time.time()
            timetopLeft += topLeftEnd - topLeftStart
            inZoneTime = 0
        
        
        
    #top left
    if (headcoord[-1][0] - circleDict['topleft']['x'])**2 + (headcoord[-1][1] - circleDict['topleft']['y'])**2 <= circleDict['topleft']['r']**2 and topLeft == False:
        print 'TOP LEFT'
        cv2.circle(frame, (circleDict['topleft']['x'], circleDict['topleft']['y']), circleDict['topleft']['r'], (0,0,255),2)
        topLeft = True
        topLeftStart = time.time()
#        inZone = True
        inZoneTime = time.time()
        
        
    if botRight == True:
        if (headcoord[-1][0] - circleDict['bottomright']['x'])**2 + (headcoord[-1][1] - circleDict['bottomright']['y'])**2 <= circleDict['bottomright']['r']**2:
            cv2.circle(frame, (circleDict['bottomright']['x'], circleDict['bottomright']['y']), circleDict['bottomright']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > ZoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendstring('11off')
        else:
            botRight = False
            botRightEnd = time.time()
            timebotRight += botRightEnd - botRightStart
            inZoneTime = 0
    #bottom right
    if (headcoord[-1][0] - circleDict['bottomright']['x'])**2 + (headcoord[-1][1] - circleDict['bottomright']['y'])**2 <= circleDict['bottomright']['r']**2 and botRight == False:
        cv2.circle(frame, (circleDict['bottomright']['x'], circleDict['bottomright']['y']), circleDict['bottomright']['r'], (0,0,255),2)
        botRight = True
        botRightStart = time.time()
        inZoneTime = time.time()
        
        
    if botLeft == True:
        if (headcoord[-1][0] - circleDict['bottomleft']['x'])**2 + (headcoord[-1][1] - circleDict['bottomleft']['y'])**2 <= circleDict['bottomleft']['r']**2:
            cv2.circle(frame, (circleDict[bottomleft]['x'], circleDict[bottomleft]['y']), circleDict[bottomleft]['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > ZoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendstring('10off')
        else:
            botLeft = False
            botLeftEnd = time.time()
            timebotLeft += botLeftEnd - botLeftStart
            inZoneTime = 0
    #bottom left
    if (headcoord[-1][0] - circleDict['bottomleft']['x'])**2 + (headcoord[-1][1] - circleDict['bottomleft']['y'])**2 <= circleDict['bottomleft']['r']**2 and botLeft == False:
        cv2.circle(frame, (circleDict['bottomleft']['x'], circleDict['bottomleft']['y']), circleDict['bottomleft']['r'], (0,0,255),2)
        botLeft = True
        botLeftStart = time.time()
        inZoneTime = time.time()
        
    if topRight == True:
        if (headcoord[-1][0] - circleDict['topright']['x'])**2 + (headcoord[-1][1] - circleDict['topright']['y'])**2 <= circleDict['topright']['r']**2:
            cv2.circle(frame, (circleDict['topright']['x'], circleDict['topright']['y']), circleDict['topright']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > ZoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendstring('12off')
        else:
            topRight = False
            topRightEnd = time.time()
            timetopRight += topRightEnd - topRightStart
            inZoneTime = 0
    #top right
    if (headcoord[-1][0] - circleDict['topright']['x'])**2 + (headcoord[-1][1] - circleDict['topright']['y'])**2 <= circleDict['topright']['r']**2 and topRight == False:
        cv2.circle(frame, (circleDict['topright']['x'], circleDict['topright']['y']), circleDict['topright']['r'], (0,0,255),2)
        topRight = True
        topRightStart = time.time()
        inZoneTime = time.time()
        
    if midCenter == True:
        if (headcoord[-1][0] - circleDict['middle']['x'])**2 + (headcoord[-1][1] - circleDict['middle']['y'])**2 <= circleDict['middle']['r']**2:
            cv2.circle(frame, (circleDict['middle']['x'], circleDict['middle']['y']), circleDict['middle']['r'], (0,0,255),2)
            inZoneTime += time.time() - inZoneTime
            if inZoneTime > ZoneTime and valve9ON == True: #if the mouse has been at this valve for X amount of seconds and the valve is also ON
                sendstring('13off')
        else:
            midCenter = False
            midCenterEnd = time.time()
            timemidCenter += midCenterEnd - midCenterStart
            inZoneTime = 0
    #center
    if (headcoord[-1][0] - circleDict['middle']['x'])**2 + (headcoord[-1][1] - circleDict['middle']['y'])**2 <= circleDict['middle']['r']**2 and midCenter == False:
        cv2.circle(frame, (circleDict['middle']['x'], circleDict['middle']['y']), circleDict['middle']['r'], (0,0,255),2)
        midCenter = True
        midCenterStart = time.time()
        inZoneTime = time.time()        
        
    f.write(str(headcoord[-1]))
    f.write('|')
    f.write(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
    f.write('\n')
            
    # draw the text and timestamp on the frame
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 226), 1)
        

    
    
    # draws mouse contours
#    cv2.drawContours(frame, cnts2, -1, (255,255,0), 3)
    cv2.imshow("Main", frame)
#    cv2.imshow("Mai2n", frameDelta)
#    cv2.imshow("Thresh2", thresh2)
#    cv2.imshow("Thresh", thresh)
#    cv2.imshow("Thresh2", thresh2)
#    cv2.imshow("Frame Delta", frameDelta)
#    cv2.imwrite('low.jpg', frame)
#    cv2.imwrite('high.jpg', frameDelta)
#    cv2.imshow("difference", difference)









    # if the `esc` key is pressed, break from the loop
    #also breaks when program exceeds 'endtime' amount of time
    key = cv2.waitKey(7) % 0x100
    if key == 27 or key == 10 or (time.time() - start) > endTime:
        #if the mouse is still at the valve when the time ends or esc is pressed
        if topLeft == True:
            topLeft = False
            topLeftEnd = time.time()
            timetopLeft += topLeftEnd - topLeftStart
            sendstring('9off')
        if botRight == True:
            botRight = False
            botRightEnd = time.time()
            timebotRight += botRightEnd - botRightStart
            sendstring('11off')
        if botLeft == True:
            botLeft = False
            botLeftEnd = time.time()
            timebotLeft += botLeftEnd - botLeftStart
            sendstring('10off')
        if topRight == True:
            topRight = False
            topRightEnd = time.time()
            timetopRight += topRightEnd - topRightStart
            sendstring('12off')
        if midCenter == True:
            midCenter = False
            midCenterEnd = time.time()
            timemidCenter += midCenterEnd - midCenterStart    
            sendstring('13off')                     
            
        stopvalve = True
        print start
        end = time.time()
        print end
        print(end - start), 'seconds'
#        f.write(str(headcoord[-1]))
#        f.write('\n')
        print 'timetopLeft', timetopLeft
        print 'timetopRight', timetopRight
        print 'timebotLeft', timebotLeft
        print 'timebotRight', timebotRight
        print 'timemidCenter', timemidCenter
        print circleDict
        cv2.imwrite('low.jpg', frame)
        cv2.imwrite('high.jpg', frameDelta)
        f.close()
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
