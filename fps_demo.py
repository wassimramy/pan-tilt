# USAGE
# python fps_demo.py
# python fps_demo.py --display 1

# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from time import sleep
import serial
import argparse
import imutils
import cv2
import sys

# new

servoTiltPos = 90
servoPanPos = 90

ser = serial.Serial('/dev/ttyACM0', 9600)
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# grab a pointer to the video stream and initialize the FPS counter
print("[INFO] sampling frames from webcam...")
stream = cv2.VideoCapture(1)
width = stream.get(3)
height = stream.get(4)
fps = FPS().start()

#

midScreenX = width / 2
midScreenY = height / 2
servoStep = 1
tol = 40

# loop over some frames
while fps._numFrames < args["num_frames"]:
	# grab the frame from the stream
	(grabbed, frame) = stream.read()

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	faces = faceCascade.detectMultiScale(
		gray,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(30, 30),
		flags=cv2.cv.CV_HAAR_SCALE_IMAGE
	)

	# If a face is detected

	if len(faces) > 0:
		cv2.rectangle(frame, (faces[0][0], faces[0][1]), (faces[0][0]+faces[0][2], faces[0][1]+faces[0][3]), (0, 255, 0), 2)
		midFaceX = faces[0][0] + (faces[0][2] / 2)
		midFaceY = faces[0][1] + (faces[0][3] / 2)
		# Check face position in relation to screen mid
		if midFaceY < midScreenY - tol:
			if servoTiltPos <= 175:
				servoTiltPos += servoStep
		elif midFaceY > midScreenY + tol:
			if servoTiltPos >= 5:
				servoTiltPos -= servoStep
		if midFaceX < midScreenX - tol:
			if servoPanPos <= 175:
				servoPanPos += servoStep
		elif midFaceX > midScreenX + tol:
			if servoPanPos >= 5:
				servoPanPos -= servoStep
				
		print('Tilt pos' + str(servoTiltPos))
		print('Pan pos' + str(servoPanPos))
		ser.write('t'+str(servoTiltPos)+'\n')
		ser.write('p'+str(servoPanPos)+'\n')
		sleep(0.1)

	# Draw a rectangle around the faces
	#for (x, y, w, h) in faces:
	#	cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
	#	send = (x*180)/400
	#	#print(str(send))
	#	#ser.write('p'+str(send)+'\n')
	#	sleep(.1)



	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# update the FPS counter
	fps.update()
	

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
stream.release()
cv2.destroyAllWindows()

# created a *threaded *video stream, allow the camera senor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

# loop over some frames...this time using the threaded stream
while fps._numFrames < args["num_frames"]:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
