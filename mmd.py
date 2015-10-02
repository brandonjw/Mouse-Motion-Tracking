'''
 USAGE WinPython command prompt
 python mmd.py
 python mmd.py --video videos/example_01.avi
 python mmd.py -v output.avi
'''
import argparse
import datetime
import time
import cv2
import numpy as np

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
f=file('mmd4.txt','w')

textcolor=(0,0,255) #red
textcolor2=(0,255,0) #green
textcolor3=(255,0,0)# dark blue
circlecolor=(0,255,0) #green
circlecolor2=(255,0,0) #dark blue
circlecolor3=(0,0,255) #red
circlecolor4=(255,255,150) #light cucumber

#initializers
headcoord=[(0,1), (1,2), (3,4)]

def findcenter(contours):
    (x,y),radius = cv2.minEnclosingCircle(contours)
    center = (int(x),int(y))
    radius = int(radius)
    return center , radius
def highestlowestXY(list):
    sortedcordlist=sorted(list) #sort by x values
    sortedcordlist2=sorted(list, key=lambda x: (x[0][1], x[0][0])) #sort by y values
    return sortedcordlist, sortedcordlist2
def boundingrect(contours): #returns coord array of bounding box
    rect = cv2.minAreaRect(contours) 
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    return box
    
def drawcoord(frame,coord,radius,circlecolor,textcolor):
    cv2.circle(frame,coord,radius/20,circlecolor,2)
    cv2.putText(frame , str(coord), coord,cv2.FONT_HERSHEY_SIMPLEX, .5,textcolor)
    
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

# loop over the frames of the video
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # convert frame to grayscale, and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 15, 255, cv2.THRESH_BINARY)[1] #low threshold
    thresh2 = cv2.threshold(frameDelta, 40, 255, cv2.THRESH_BINARY)[1] #higher theshold

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=1)
    thresh2 = cv2.dilate(thresh2, None, iterations=1)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    (cnts2, _) = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  

    # loop over the contours
    #low threshold
    for c in cnts:
        center,radius = findcenter(c)
        
        if center == (560,405): #won't need this if you have first frame with NO mouse
            continue
        if center[0] == 560:
            continue
        if center[0] == 561:
            continue

        box = boundingrect(c)
        
#        im = cv2.drawContours(frame,[box],0,(0,0,255),2) #draw bounding rect
#        for x,y in box:
#            drawcoord(frame,(x,y),radius,circlecolor, textcolor)

    # loop over the contours
    #high threshold
    for c2 in cnts2:
        clist2 = c2.tolist()
        sortedcordlist, sortedcordlist2 = highestlowestXY(clist2)
        center2, radius2 = findcenter(c2)
        
        if center2[0] == 558: #won't need this if you have first frame with NO mouse
            continue

        box2 = boundingrect(c2)
        
#        im2 = cv2.drawContours(frame,[box2],0,circlecolor4,2)  #draw bounding rect
#        for x,y in box2:
#            drawcoord(frame,(x,y),radius,circlecolor2, textcolor2)
        
    boxdifference = box-box2 #subtracts the verticies of higher threshold from lower threshold bounding rects
    sumofbox = sum(boxdifference) #finds the total change in each dimension 
    
    #if total change in x is greater than y
    if abs(sumofbox[0]) > abs(sumofbox[1]): 
        if sumofbox[0] > 0: #if change in x is pos
            coord1 = (sortedcordlist[0][0][0],sortedcordlist[0][0][1])
            headcoord.append(coord1) #append the smallest x contour
        else: #if change in x is neg
            coord2 = (sortedcordlist[-1][0][0],sortedcordlist[-1][0][1])
            headcoord.append(coord2) #append the highest x contour
            
    #if total change in x is less than y
    if abs(sumofbox[0]) < abs(sumofbox[1]): 
        if sumofbox[1] > 0: #if change in y is pos
            coord3 = (sortedcordlist2[0][0][0],sortedcordlist2[0][0][1])
            headcoord.append(coord3)
        else: #if change in y is neg
            coord4 = (sortedcordlist2[-1][0][0],sortedcordlist2[-1][0][1])
            headcoord.append(coord4)
            
    if headcoord[-1] == (515,417): #won't need this if you have first frame with NO mouse
        continue
    if headcoord[-1] == (515,418):
        continue
    #draws head coord
    drawcoord(frame,headcoord[-1],radius2,circlecolor, textcolor)    
            
    # draws the text and timestamp on the frame
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 226), 1)
        
    # draws mouse contours
#    cv2.drawContours(frame, cnts2, -1, (255,255,0), 3)
        
    #shows the frame
    cv2.imshow("Main", frame)
#    cv2.imshow("Thresh", thresh)
#    cv2.imshow("Thresh2", thresh2)
#    cv2.imshow("Frame Delta", frameDelta)
    cv2.imwrite('low.jpg', frame)
    cv2.imwrite('high.jpg', frameDelta)

    # if the `esc` key is pressed, break from the loop
    key = cv2.waitKey(7) % 0x100
    if key == 27 or key == 10:
#        for cord in estheadcoordlist:
#            f.write(str(cord))
#            f.write('\n')
        f.close()
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
