#!/usr/bin/env python
from gpio_utils import *
from Constants import *
from rTSL2561 import *
from rBME280 import *
import socket
import time
import csv
import threading
import sys
import os
from rMemini import *
from rPixieLog import pixieLog
import logging

from rawADC import readADC
from Audio import audioFeatureExt
from MotionFeature import motionFeatExt

from threading import Lock

IS_MEMINI = False
IS_PIXIE = False

# True when testing relay without basestation
NO_BASESTATION_TEST = False


# get BS IP and RS port # from config file
configFileName = r'/root/besi-relay-station/BESI_LOGGING_R/config'
#configDirName = os.path.dirname(configFileName)
#os.chdir(configDirName)
fconfig = open(configFileName)
for line in fconfig:
	if line[0] == "#":
		pass
	else:
		splitLine = line.split("=")
		try:
			if splitLine[0] == "BaseStation_IP":
				BaseStation_IP2 = str(splitLine[1]).rstrip()
		except:
			print "Error reading IP Address"
		
		try:
			if splitLine[0] == "relayStation_ID":
				relayStation_ID2 = int(splitLine[1])
		except:
			print "Error reading Port" 

		try:
			if splitLine[0] == "Wearable":
				wearable_mode = str(splitLine[1]).rstrip()
				if wearable_mode=="Pixie":
					IS_PIXIE = True
					IS_MEMINI = False
				elif wearable_mode=="Memini":
					IS_PIXIE = False
					IS_MEMINI = True
		except:
			print "Error finding Pebble Mode"

		# if IS_PIXIE == True:
		try:
			if splitLine[0] == "PebbleFolder":
				PebbleFolder = str(splitLine[1]).rstrip()
		except:
			print "Error reading Pebble Folder"




default_settings = ''
fconfig.close()
# create local data folder - not needed if using SD card
#if not os.path.exists("Data"):
#	os.mkdir("Data")
# create data storage files
baseFolder = BASE_PATH+"Relay_Station{}/".format(relayStation_ID2)
if not os.path.exists(baseFolder):
	os.mkdir(baseFolder)
#if not os.path.exists(baseFolder + "Accelerometer"):
#	os.mkdir(baseFolder + "Accelerometer")
if not os.path.exists(baseFolder + "Temperature"):
	os.mkdir(baseFolder + "Temperature")
if not os.path.exists(baseFolder + "Light"):
	os.mkdir(baseFolder + "Light")
if not os.path.exists(baseFolder + "Audio"):
	os.mkdir(baseFolder + "Audio")
# if not os.path.exists(baseFolder + "Door"):
# 	os.mkdir(baseFolder + "Door")
if not os.path.exists(baseFolder + "Weather"):
	os.mkdir(baseFolder + "Weather")

if not os.path.exists(baseFolder + "rawADC"):
	os.mkdir(baseFolder + "rawADC")
if not os.path.exists(baseFolder + "AudioF"):
	os.mkdir(baseFolder + "AudioF")
if not os.path.exists(baseFolder + "Door"):
	os.mkdir(baseFolder + "Door")
if not os.path.exists(baseFolder + "Direction"):
	os.mkdir(baseFolder + "Direction")

if not os.path.exists(baseFolder + "rawPebble"): #for Pebble data that's done with featExt
	os.mkdir(baseFolder + "rawPebble")
if not os.path.exists(baseFolder + "PebbleFeature"): #for Pebble data that's done with featExt
	os.mkdir(baseFolder + "PebbleFeature")

if IS_PIXIE == True:
	if not os.path.exists(BASE_PATH + PebbleFolder): #for Pebble data that's done with featExt
		os.mkdir(BASE_PATH + PebbleFolder)

print ("Default Settings:")
print ("Base Station IP Address: {0}".format(BaseStation_IP2))
print ("Relay Station ID: {0}".format(relayStation_ID2))
print ("Pebble Mode: {0}".format(wearable_mode))
if IS_PIXIE == True:
	print ("PebbleFolder: {0}".format(PebbleFolder))


hostIP = BaseStation_IP2
BASE_PORT = relayStation_ID2 

# lock = threading.allocate_lock()

while True:
	
	# Testing relay w/o basestation
	if NO_BASESTATION_TEST:
		startDateTime = "2018-08-21 00:00:00.000"
		USE_LIGHT = False
		USE_ADC = False
		USE_WEATHER = False
		USE_AUDIO = False
		USE_DOOR = False

		IS_PIXIE = True
		IS_MEMINI = False

	else:
		# IS_STREAMING is always True
		if IS_STREAMING:
			synchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_address_synch = (hostIP, BASE_PORT)
			synchSock.settimeout(10)
			#print "connecting to %s port %s" % server_address_synch
			try:
				synchSock.connect(server_address_synch)
			except:
				print "connection to base station timed out"
				time.sleep(5)
				continue
			print "Connected to {} port {}".format(hostIP, BASE_PORT)	
			synchSock.settimeout(None)
			synchSock.sendall("starting up")		
			# receive info
			# get 3 byte length first
			msgLen = ''
			while (len(msgLen) != 3):
				try:
					msgLen = msgLen + synchSock.recv(3)
				except:
					pass

			msgLen = int(msgLen)
			data = ''    
			# call recv until we get all the data
			while (len(data) != msgLen):
				try:
					data = data + synchSock.recv(msgLen)
				except:
					pass
			# Base Station sends Shimmer BT IDs and start time
			splitData = data.split(";")

			startDateTime = splitData[2]
			USE_LIGHT = True
			USE_ADC = False
			USE_WEATHER = True
			USE_AUDIO = False
			USE_DOOR = False #door got moved to rawADC.py thread

			# USE_LIGHT = False
			# USE_ADC = False
			# USE_WEATHER = False
			# USE_AUDIO = False
			# USE_DOOR = False
			# IS_PIXIE = False
			# IS_MEMINI = False

					#startDateTime = "2017-08-25 12:30:01 EDT"
			#print startDateTime

			synchSock.close()

	ferror = open("error", "a")

	#stream to base station 
	if IS_STREAMING:		   		

		if USE_LIGHT:
			lightThread = threading.Thread(target=lightSense, args=(startDateTime, hostIP, BASE_PORT, IS_STREAMING, IS_LOGGING))
			lightThread.setDaemon(True)
			
		if USE_ADC:
			ADCThread = threading.Thread(target=readADC, args = (startDateTime, hostIP, BASE_PORT, IS_STREAMING, IS_LOGGING))
			ADCThread.setDaemon(True)
		
		if USE_WEATHER:
			weatherThread = threading.Thread(target=weatherSense, args=(startDateTime,hostIP,BASE_PORT))
			weatherThread.setDaemon(True)

		if USE_AUDIO:
			audioThread = threading.Thread(target=audioFeatureExt, args = (startDateTime, hostIP, BASE_PORT))
			audioThread.setDaemon(True)

		if IS_MEMINI:
			meminiThread = threading.Thread(target=meminiSense, args=(startDateTime,hostIP,BASE_PORT,Lock()))
			meminiThread.setDaemon(True)

		if IS_PIXIE:        
			pass 
			# # Pebble - Pixie Logging 
			# pixieThread = threading.Thread(target=pixieLog, args=(startDateTime,hostIP,BASE_PORT, PebbleFolder))
			# pixieThread.setDaemon(True)
			# # Pebble Feature Ext + Stream to BaseStation
			# pebbleFeatThread = threading.Thread(target=motionFeatExt, args = (startDateTime, hostIP, BASE_PORT, PebbleFolder))
			# pebbleFeatThread.setDaemon(True)

				




	# trap keyboard interrupt
	try:
		if USE_LIGHT:
			lightThread.start()
		if USE_ADC:
			ADCThread.start()
		if USE_WEATHER:
			weatherThread.start()
		if IS_MEMINI:
			meminiThread.start()
		if IS_PIXIE:
			pass
			# pixieThread.start()
			# pebbleFeatThread.start()

		if USE_AUDIO:
			audioThread.start()

		# wait until every thread exits (should never happen)
		if USE_LIGHT:
			lightThread.join()
		if USE_ADC:
			ADCThread.join()
		if USE_WEATHER:
			weatherThread.join()
		if IS_MEMINI:
			meminiThread.join()
		if IS_PIXIE:
			pass
			# pixieThread.join()
			# pebbleFeatThread.join()
		
		if USE_AUDIO:
			audioThread.join()
	
	except:
		print ""
		print "Exit"
