from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import time
import csv
import subprocess
import sys

def main():
	readADC()

def readConfigFile():
	# get BS IP and RS port # from config file
	configFileName = r'/root/besi-relay-station/BESI_LOGGING_R/config'
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
			# try:
			# 	if splitLine[0] == "PebbleFolder":
			# 		PebbleFolder = str(splitLine[1]).rstrip()
			# except:
			# 	print "Error reading Pebble Folder"
			# try:
			# 	if splitLine[0] == "Wearable":
			# 		wearable_mode = str(splitLine[1]).rstrip()
			# 		if wearable_mode=="Pixie":
			# 			IS_PIXIE = True
			# 			IS_MEMINI = False
			# 		elif wearable_mode=="Memini":
			# 			IS_PIXIE = False
			# 			IS_MEMINI = True
			# except:
			# 	print "Error finding Pebble Mode"

			# if IS_PIXIE == True:
				
	default_settings = ''
	fconfig.close()

	return BaseStation_IP2, relayStation_ID2
	
# gets sensor values from the temperature sensor and the microphone, writes the data to a file and sends the data over a socket
# def readADC(startDateTime, hostIP, BASE_PORT, streaming = True, logging = True):
def readADC():
	streaming = True
	logging = True

	#get info from config file
	hostIP, BASE_PORT = readConfigFile()

	server_address = (hostIP, BASE_PORT)

	startDateTime = rNTPTime.sendUpdate(server_address, "-99", 5)
	while startDateTime == None:
		time.sleep(3)
		startDateTime = rNTPTime.sendUpdate(server_address, "-99", 5)
	if startDateTime != None:
		# use custom function because datetime.strptime fails in multithreaded applications
		startTimeDT = rNTPTime.stripDateTime(startDateTime)
	
	audioFileName = BASE_PATH+"Relay_Station{0}/Audio/Audio{1}.txt".format(BASE_PORT, startTimeDT)
	# doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
	# tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
	
	global rawADC_Time
	global rawADC_startDateTime
	rawADC_startDateTime = startDateTime

	sensoMessage = " ADC "

	rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)
	with open(rawADCFileName, "w") as rawADCFile:
		rawADCFile.write(startDateTime+"\n")
		rawADCFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		rawADCFile.write("Timestamp,Mic(10kHz samples)\n")
	# rawADCFile.close()

	doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
	with open(doorFileName, "w") as doorFile:
		doorFile.write(startDateTime+"\n")
		doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
	# doorFile.close()
		
	tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
	with open(tempFileName, "w") as tempFile:
		tempFile.write(startDateTime+"\n")
		tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
		tempFile.write("Timestamp,Degree F\n")
	# tempFile.close()
		
	# get starting time according to the BBB. This is only used for time deltas
	startTime = datetime.datetime.now()
	
	iterationsAudio = 0
	iterations = 0
	dummyvar = 0

	test_count = 0
	
	sumAudio = 0
	sumDoor1 = 0
	sumDoor2 = 0
	sumTemp = 0

	while True:

		rawADC_Time = startTimeDT
		if iterationsAudio >= AUDIO_LENGTH:

			iterationsAudio = 0

			test_count += 1
			# startDateTime = "2017-11-15 %d%d:%d%d:%d%d.000" %(test_count,test_count,test_count,test_count,test_count,test_count)

			#get current time from basestation
			startDateTime = rNTPTime.sendUpdate(server_address, "-99", 5)
			# if startDateTime updates sucessfully -> create a new file
			# if startDateTime == None (update fails) -> keep writing the current file
			if startDateTime != None:
				startTimeDT = rNTPTime.stripDateTime(startDateTime)
				rawADC_Time = startTimeDT
				rawADC_startDateTime = startDateTime

				rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)
				with open(rawADCFileName, "w") as rawADCFile:
					rawADCFile.write(startDateTime+"\n")
					rawADCFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					rawADCFile.write("Timestamp,Mic(10kHz samples)\n")
				rawADCFile.close()

				# get new local start time
				startTime = datetime.datetime.now()		
		iterationsAudio += 1

		if iterations >= FILE_LENGTH:

			iterations = 0

			# test_count += 1
			# startDateTime = "2017-11-15 %d%d:%d%d:%d%d.000" %(test_count,test_count,test_count,test_count,test_count,test_count)

			#get current time from basestation
			startDateTime = rNTPTime.sendUpdate(server_address, "-99", 5)
			# if startDateTime updates sucessfully -> create a new file
			# if startDateTime == None (update fails) -> keep writing the current file
			if startDateTime != None:
				startTimeDT = rNTPTime.stripDateTime(startDateTime)

				doorFileName = BASE_PATH+"Relay_Station{0}/Door/Door{1}.txt".format(BASE_PORT, startTimeDT)
				with open(doorFileName, "w") as doorFile:
					doorFile.write(startDateTime+"\n")
					doorFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					doorFile.write("Timestamp,Door Sensor Channel 1, Door Sensor Channel 2\n")
				# doorFile.close()
					
				tempFileName = BASE_PATH+"Relay_Station{0}/Temperature/Temperature{1}.txt".format(BASE_PORT, startTimeDT)
				with open(tempFileName, "w") as tempFile:
					tempFile.write(startDateTime+"\n")
					tempFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					tempFile.write("Timestamp,Degree F\n")
				# tempFile.close()

				# get new local start time
				startTime = datetime.datetime.now()
		iterations += 1


		dummyvar += 1
		
		# calculate the time since the start of the data collection
		currTime = datetime.datetime.now()
		currTimeDelta = (currTime - startTime).days * 86400 + (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
			
		# run the c code to get one second of data from the ADC
		proc = subprocess.Popen(["./root/besi-relay-station/BESI_LOGGING_R/ADC1"], stdout=subprocess.PIPE,)
		# proc = subprocess.Popen(["./ADC1"], stdout=subprocess.PIPE,)
		# anything printed in ADC.c is captured in output
		output = proc.communicate()[0]
		split_output = output.split(',')
		# for new relay library (debian 9.5)
		split_output[0] = split_output[1]
		# try:
		# 	proc = subprocess.Popen(["./ADC1"], stdout=subprocess.PIPE,)
		# 	# anything printed in ADC.c is captured in output
		# 	output = proc.communicate()[0]
		# 	split_output = output.split(',')
		# except :
		# 	print "Thread: ADCThread, ERROR: subprocess.Popen[./ADC1]"
		# 	split_output = [0]*10021
		# 	split_output = ",".join(map(str, split_output))
		# 	split_output = split_output.split(',')


		# print newTimeDelta, (float(split_output[-5]) + currTimeDelta - testTime), len(split_output)
			
		# data is in <timestamp>,<value> format
		# 100 samples/second from the mic and 1 sample/sec from the temperature sensor
		i = 0 
		ka = 0
		sumA = 0
		kd = 0

		(tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)

		buffer_size = 2048
		with open(rawADCFileName, "a", buffer_size) as rawADCFile:

			rawADCFile.write("%0.4f," %(currTimeDelta))
			rawADCFile.write(",".join(split_output[0:10000]) + ",")
			rawADCFile.write("\n")
			# rawADCFile.write(",".join(split_output[10000:10010]) + ",")
			# rawADCFile.write(",".join(split_output[10010:10020]) + ",")
			# rawADCFile.write("%03.2f" %(tempF))
		# rawADCFile.close()

		doorData = map(float,split_output[10000:10020])
		sumDoor1 = sumDoor1 + sum(doorData[0:10])
		sumDoor2 = sumDoor2 + sum(doorData[10:20])

		with open(doorFileName, "a") as doorFile:
			for i in range(0,10):
				doorFile.write("%0.2f," %( currTimeDelta + (0.1*i) ))
				doorFile.write("%0.4f," %( doorData[i]))
				doorFile.write("%0.4f\n" %( doorData[i+10]))
		# doorFile.close()

		with open(tempFileName, "a") as tempFile:
			tempFile.write("%0.2f," %( currTimeDelta ))
			tempFile.write("%03.2f\n" %(tempF))
		# tempFile.close()

		# newTime = datetime.datetime.now()
		# newTimeDelta = (newTime - currTime).days * 86400 + (newTime - currTime).seconds + (newTime - currTime).microseconds / 1000000.0

		# testTime = float(split_output[-5]) + currTimeDelta
		if (iterations%UPDATE_LENGTH)==(UPDATE_LENGTH-2):
			# iterations = 0
			doorMessage = []
			doorMessage.append("Door")
			doorMessage.append(str("{0:.3f}".format(sumDoor1))) #channel1
			doorMessage.append(str("{0:.3f}".format(sumDoor2))) #channel2
			tempDateTime = rNTPTime.sendUpdate(server_address, doorMessage, 5) #Audio uses startDateTime from rawADC
			sumDoor1 = 0
			sumDoor2 = 0

			tempMessage = []
			tempMessage.append("Temperature")
			tempMessage.append(str("{0:.3f}".format(tempF))) #tempF
			tempDateTime = rNTPTime.sendUpdate(server_address, tempMessage, 5) #Audio uses startDateTime from rawADC
			


# do stuff in main() -- for 'after declare' function
if __name__ == '__main__':
	main()
