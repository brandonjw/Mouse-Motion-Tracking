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

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
#f=file('coord22.txt','w')
img = None
coordtext = None
xgreater = False
xless = False
ygreater = False
yless = False
#this list will contain the coords for the center of the mouse in each frame. this allows you to compare center cords, recent vs present
#the initial values act as initializers
centerlist=[(0,1),(2,3),(4,5),(5,6),(7,8)]

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
    thresh = cv2.threshold(frameDelta, 40, 255, cv2.THRESH_BINARY)[1] #higher theshold
#    thresh = cv2.threshold(frameDelta, 12, 255, cv2.THRESH_BINARY)[1] #low threshold

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=1)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
  

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        
        #convert c, which is an array, to a list
        clist=c.tolist()
        sortedcordlist=sorted(clist) #sort by x values
        sortedcordlist2=sorted(clist, key=lambda x: (x[0][1], x[0][0])) #sort by y values
        
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
        
        #finds the center of the mouse
        (x,y),radius = cv2.minEnclosingCircle(c)
        center = (int(x),int(y))
        radius = int(radius)
        
        if center == (558,421): #won't need this if you have first frame with NO mouse
            continue
        if center[0] == 558:
            continue
        
#        f.write(str(center))
#        f.write('\n')
        
        #bounding rectangle
#        (x, y, w, h) = cv2.boundingRect(c)
#        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#        comma=','
#        jointhis=(str(x),str(y))
#        comma.join(jointhis)
#        cv2.putText(frame , comma.join(jointhis), (x,y),cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,255))      
        
        
        #tries to solve mouse standing still problem
        #subtracts the present x coord from the fourth to last frame's x value
        group1=abs(center[0] - centerlist[-4][0])
        
#        subtracts the present y coord from the fourth to last frame's y value
        group2=abs(center[1] - centerlist[-4][1])
        
#        the mindset here is that if the change in both x and y values are less than 5, then the mouse is standing still
        #if standing still, then make it so that the head cords do not move
        if abs(group1-group2) < 5:
#            print 'standing still'
            img3 = cv2.circle(frame,center,radius/20,(0,255,0),2)
            cv2.putText(frame , str(center), center,cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,255))
            centerlist.append(center)
            
            if xgreater == True:
                img = cv2.circle(frame,coord34,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord34str, coord34,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
            if xless == True:
                img = cv2.circle(frame,coord12,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord12str, coord12,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
            if ygreater == True:
                img = cv2.circle(frame,coord78,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord78str, coord78,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
            if yless == True:
                img = cv2.circle(frame,coord56,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord56str, coord56,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
            continue
            #             x value                          y value               if greater change in x value versus y value...
        if abs(center[0] - centerlist[-1][0]) > abs(center[1] - centerlist[-1][1]): #compares present x and y values, compared to their respective recent past values
            if center[0] > centerlist[-1][0]:#if present center x value is greater than previous x value... want highest x value
                img = cv2.circle(frame,coord34,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord34str, coord34,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
#                print 'moving'
                xgreater = True
                xless = False
                ygreater = False
                yless = False
            else:
                img = cv2.circle(frame,coord12,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord12str, coord12,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
#                print 'moving'
                xgreater = False
                xless = True
                ygreater = False
                yless = False
        else:
            if center[1] > centerlist[-1][1]: #if present center y value is greater than previous y value, you want the higher y value
                img = cv2.circle(frame,coord78,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord78str, coord78,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
#                print 'moving'
                xgreater = False
                xless = False
                ygreater = True
                yless = False
            else:
                img = cv2.circle(frame,coord56,radius/20,(255,200,0),2)
                coordtext = cv2.putText(frame , coord56str, coord56,cv2.FONT_HERSHEY_SIMPLEX, .5,(130,70,180))
#                print 'moving' 
                xgreater = False
                xless = False
                ygreater = False
                yless = True
                
        centerlist.append(center)

        
#        show center circle + coord text        
    
        img3 = cv2.circle(frame,center,radius/20,(0,255,0),2)
        cv2.putText(frame , str(center), center,cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,255))
        
    # draw the text and timestamp on the frame
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 226), 1)

    # draws mouse contours
#    cv2.drawContours(frame, cnts, -1, (255,255,0), 3)

    cv2.imshow("Main", frame)
    cv2.imshow("Thresh", thresh)
#    cv2.imshow("Frame Delta", frameDelta)
#    cv2.imwrite('frame4945.jpg', frame)

    # if the `esc` key is pressed, break from the loop
    key = cv2.waitKey(7) % 0x100
    if key == 27 or key == 10:
#        f.close()
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
