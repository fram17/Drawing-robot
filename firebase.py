import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageFilter
import PIL.ImageOps    
import subprocess
import time
import sys
import pyrebase
import json
import serial
with open('config.json') as config_file:
    config = json.load(config_file)

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
db = firebase.database()
state = 1
def stream_handler(message):

	cloudPath = '/Picture/1.jpg'
	storage.child(cloudPath).download("imageDownload/download2.jpg")
	img = cv2.imread('imageDownload/download2.jpg')
	img = cv2.resize(img, None, fx=0.2, fy=0.2) # resize since image
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	retval, thresh_gray = cv2.threshold(gray, thresh=120, maxval=255, type=cv2.THRESH_BINARY)
	points = np.argwhere(thresh_gray==0) # find where the black pixels are
	points = np.fliplr(points) # store them in x,y coordinates instead of row,col indices
	x, y, w, h = cv2.boundingRect(points) # create a rectangle around those points
	x, y, w, h = x-5, y-5, w+5, h+5 # make the box a little bigger
	crop = gray[y:y+h, x:x+w] # create a cropped region of the gray image
	retval, thresh_crop = cv2.threshold(crop, thresh=120, maxval=255, type=cv2.THRESH_BINARY)
	plt.imsave('000.png', thresh_gray, cmap='gray')
	im=Image.open("000.png")
	im.save("000.bmp")
	#subprocess.call(['potrace','000.bmp','-s','-o','newsvg.svg'])
	subprocess.call(['autotrace','000.bmp','-centerline','-output-file','000.svg'])
	svg = open('000.svg', 'r')
	newsvg = open('newsvg.svg','w')
	state_svg = 0
	splitSVG = []
	for i in svg :
		if state_svg == 1:
			splitSVG = i.split(' ', 1)
			#print(splitSVG)
			newLines = splitSVG[0] + ' xmlns="http://www.w3.org/2000/svg" ' + splitSVG[1]
			#print(newLines)
			newsvg.write(newLines)
		else:
			newsvg.write(i)
		state_svg +=1
	
	svg.close()
	newsvg.close()
		
	storage.child("SVG/1.svg").put("newsvg.svg")

	#Genalate G-code
	subprocess.call('juicy-gcode newsvg.svg --output TESTG2.gcode',shell=True)

	f = open('TESTG2.gcode', 'r')
	t = open('NewG.gcode', 'w')

	while True :
		s = f.readline()
		print('S = ', s)
		c = s.startswith('G90')
		g = s.startswith('G4')
		#time.sleep(0.2)	

		if (c == False and g == False):
			t.write(s)
			#time.sleep(0.2)
	
	
		if c == True:
			print('Detected G90','\n')
			print('Add G21')
			t.write(s)
			t.write('G21\n')
		
	
		if g == True:
			print('Skip G4')
			#time.sleep(0.2)
			break


	while True :
		s = f.readline()
		print('SS = ', s)
		d = s.startswith('G01 Z0 F10.00')
		g = s.startswith('G4')
		e = s.startswith('M5')
		print('D =',d)
		#time.sleep(0.2)

		if (d == False and g == False and e == False) :
			t.write(s)
		
		if d == True:
			print('Detected G01 Z0 F10','\n')
			print('Add G01 Z0 F500')
			t.write('G01 Z0 F700\n')

		if g == True:
			print('Skip G4')

	
		if e == True:
			t.write('G01 X0 Y0\n')
			t.write('M2\n')
			break

	print('End while loop')

	f.close()
	t.close()

	storage.child("SVG/1.svg").put("newsvg.svg")

	global state
	print(state)
        if state > 1: 
		#time.sleep(10)
		subprocess.call('python send.py',shell=True)
		state = 1
		print("Complete")
	state = state+1	
	print("Waiting")

my_stream = db.child("message").stream(stream_handler)


      


