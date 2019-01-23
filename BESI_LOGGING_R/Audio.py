from gpio_utils import *
from Constants import *
import rNTPTime
import socket
import os
import time
import csv
import subprocess
import sys
from pyAudioAnalysis import audioFeatureExtraction
import rawADC

def main():
	audioFeatureExt()

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

def audioFeatureExt():
	# def audioFeatureExt(startDateTime, hostIP, BASE_PORT):

	debugMode = True

	time.sleep((LOOP_DELAY * UPDATE_DELAY))

	hostIP, BASE_PORT = readConfigFile()

	#Heartbeat stuff
	server_address = (hostIP, BASE_PORT)

	# startDateTime = rNTPTime.sendUpdate(server_address, "-99", 10)
	# if startDateTime != None:
	# 	# use custom function because datetime.strptime fails in multithreaded applications
	# 	startTimeDT = rNTPTime.stripDateTime(startDateTime)
	# else:
	# 	while(startDateTime == None):
	# 		startDateTime = rNTPTime.sendUpdate(server_address, "-99", 10)
	# 		time.sleep(5)
	# 		print "connection to base station timed out"
	# 	startTimeDT = rNTPTime.stripDateTime(startDateTime)

	audioMessage = []
	sumAudio = 0
	sumAudioFeat = 0
	iterations = 0

	startLine = 3 #from rawADC - line0 = header, line1 = time, line2 = description
	aSamplingFreq = 10000
	winSize = 0.250 #sec
	winStep = 0.125 #sec

	audioBuffer = ["0"]

	# startTimeDT = rNTPTime.stripDateTime(startDateTime)
	# audioFeatureFileName = BASE_PATH+"Relay_Station{0}/AudioF/AudioF{1}.txt".format(BASE_PORT, startTimeDT)

	# with open(audioFeatureFileName, "w") as audioFeatureFile:
	# 	audioFeatureFile.write(startDateTime+"\n")
	# 	audioFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
	# 	audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
	# 	#audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, , ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
	# audioFeatureFile.close()

	currLine = startLine #current line to read/write from

	print "Starting Audio Thread"

	while True:
		# startTimeDT = rNTPTime.stripDateTime(startDateTime)

		rawADCLocation = BASE_PATH+"Relay_Station{0}/rawADC/".format(BASE_PORT)
		files = os.walk(rawADCLocation).next()[2] #BASE_PATH = /media/card/
		files.sort() #previous file first

		rawlineCount = 0
		# print files

		if (len(files) > 0) : #not an empty folder

			rawADC_timeStamp = files[0][6:-4] # read timeStamp on rawADC filename 
			rawADCFileName = BASE_PATH + "Relay_Station{0}/rawADC/".format(BASE_PORT) + "/" + files[0]

			#create new audio feature file
			audioFeatureFileName = BASE_PATH+"Relay_Station{0}/AudioF/AudioF{1}.txt".format(BASE_PORT, rawADC_timeStamp)
			if not os.path.exists(audioFeatureFileName):
				with open(audioFeatureFileName, "w") as audioFeatureFile:
					audioFeatureFile.write(rawADC_timeStamp+"\n")
					audioFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
					audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")


			if debugMode: print "reading lines from " + files[0]
			f = open(BASE_PATH + "Relay_Station{0}/rawADC/".format(BASE_PORT) + "/" + files[0], "r") 
			rawlineCount = 0
			for line in f.xreadlines(  ): rawlineCount += 1
			f.close()
			if debugMode: print "rawlineCount =" + str(rawlineCount)
			if debugMode: print "currLine =" + str(currLine)
		# close(rawADCFileName)

		# print "2017-08-07 %d%d:%d%d:%d%d.000" %(1,1,1,1,1,1)
		# if startTimeDT != rawADC_Time:
		# 	print "FileChanged!!!!

		# print "rawADC Size = ", rawlineCount, ", AudioFeature Size = ",currLine, ", rawADCTime = ", rawADC.rawADC_Time, ", AudioFileTime = ", startTimeDT

		# if False:
		if rawlineCount > currLine:
			rawADCFileName = BASE_PATH + "Relay_Station{0}/rawADC/".format(BASE_PORT) + "/" + files[0]
			with open(rawADCFileName, "r") as rawADCFile:
				rawADC_string = rawADCFile.readlines()[currLine:rawlineCount]
			# rawADCFile.close()

			for j in range(len(rawADC_string)):
				rawADC_Data = rawADC_string[j].split(',')
				timeDelta = float(rawADC_Data[0])
				# audioData = rawADC_Data[1:10001]
				# doorData1 = rawADC_Data[10001:10011]
				# doorData2 = rawADC_Data[10011:10021]
				# tempF = float(rawADC_Data[-1])
				if debugMode: print "len rawADC Data = "+ str(len(rawADC_Data[1:10001]))

				if (len(rawADC_Data[1:10001]) < 10000) and (currLine == (rawlineCount-1)): #rawADC file fault - last line bugged
					rawADCLocation = BASE_PATH+"Relay_Station{0}/rawADC/".format(BASE_PORT)
					files = os.walk(rawADCLocation).next()[2] #BASE_PATH = /media/card/
					files.sort() #previous file first

					if len(files) >= 2 :
						# currLine = currLine + 1
						currLine = rawlineCount
						if debugMode: print "Last line bugged - move to next file" 


				if len(rawADC_Data[1:10001]) == 10000:
					# audioFeatureExtraction.stFeatureExtraction(data, Fs, window, step)
					# F = audioFeatureExtraction.stFeatureExtraction(rawADC_Data[1:10001], aSamplingFreq,
					#  winSize*aSamplingFreq, winStep*aSamplingFreq)

					if len(audioBuffer) >= 1250: #
						F = audioFeatureExtraction.stFeatureExtraction(audioBuffer+rawADC_Data[1:10001], aSamplingFreq,
							winSize*aSamplingFreq, winStep*aSamplingFreq)
						timeDelta = timeDelta-0.125
					else: #no audio buffer - first run - just create a new file
						F = audioFeatureExtraction.stFeatureExtraction(rawADC_Data[1:10001], aSamplingFreq,
							winSize*aSamplingFreq, winStep*aSamplingFreq)

					audioBuffer = rawADC_Data[8751:10001]
					
					with open(audioFeatureFileName, "a") as audioFeatureFile:

						for i in range(0, 7):
							timeStepDelta = winStep*i
							audioFeatureFile.write("%0.4f," %(timeDelta+timeStepDelta))
							audioFeatureFile.write("%f," %(F[0,i]))
							audioFeatureFile.write("%f," %(F[1,i]))
							audioFeatureFile.write("%f," %(F[2,i]))
							audioFeatureFile.write("%f," %(F[3,i]))
							audioFeatureFile.write("%f," %(F[4,i]))
							audioFeatureFile.write("%f," %(F[5,i]))
							audioFeatureFile.write("%f," %(F[6,i]))
							audioFeatureFile.write("%f," %(F[7,i]))
							audioFeatureFile.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f,"
								%(F[8,i], F[9,i], F[10,i], F[11,i], F[12,i], F[13,i], F[14,i], F[15,i],
								 F[16,i], F[17,i], F[18,i], F[19,i], F[20,i]))
							audioFeatureFile.write("%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f,"
								%(F[21,i], F[22,i], F[23,i], F[24,i], F[25,i], F[26,i], F[27,i], F[28,i],
								 F[29,i], F[30,i], F[31,i], F[32,i]))
							audioFeatureFile.write("%f\n" %(F[33,i]))	

							sumAudio += float(F[2,i]) #data for HEART BEAT
							sumAudioFeat += float(F[3,i])

					audioFeatureFile.close()			

					sumAudio = sumAudio/7 # there's 7 windows in 1 sec
					sumAudioFeat = sumAudioFeat/7
					iterations += 1

					# currLine = currLine + 1 #move to the next Audio line
					currLine = rawlineCount
					if debugMode: print "AudioFeature Extracted" 

		#if finish audioFeature Ext + rawADC creates a new file
		elif (len(files) >= 2) : #has new rawADC file + rawlineCount == or < currLine
 		# elif rawADC.rawADC_Time != startTimeDT:
 			time.sleep(1)

			rawlineCount = 0
			for line in open(rawADCFileName).xreadlines(  ): rawlineCount += 1

			if rawlineCount<=currLine:

				if debugMode: print "finished reading "+ files[0]+", deleting file now.."
				os.remove(rawADCFileName)
				currLine = startLine

				time.sleep(1)

		elif (len(files) == 1) and (currLine==rawlineCount) :
						if debugMode: print "waiting for new data..."
						# if debugMode: print "length of rawX = " + str(len(rawX))
						time.sleep(1)
				# startDateTime = rawADC.rawADC_startDateTime
				# startTimeDT = str(rawADC.rawADC_Time)
				# audioFeatureFileName = BASE_PATH+"Relay_Station{0}/AudioF/AudioF{1}.txt".format(BASE_PORT, startTimeDT)

				# # create new audioFeatureFile
				# with open(audioFeatureFileName, "w") as audioFeatureFile:
				# 	audioFeatureFile.write(startDateTime+"\n")
				# 	audioFeatureFile.write("Deployment ID: Unknown, Relay Station ID: {}\n".format(BASE_PORT))
				# 	audioFeatureFile.write("Timestamp, ZCR, Energy, Energy Entropy, Spectral Centroid, Spectral Spread, Spectral Entropy, Spectral Flux, Spectral Rolloff, MFCC0, MFCC1, MFCC2, MFCC3, MFCC4, MFCC5, MFCC6, MFCC7, MFCC8, MFCC9, MFCC10, MFCC11, MFCC12, ChromaVector1, , ChromaVector2, ChromaVector3, ChromaVector4, ChromaVector5, ChromaVector6, ChromaVector7, ChromaVector8, ChromaVector9, ChromaVector10, ChromaVector11, ChromaVector12, ChromaDeviation\n")
				# audioFeatureFile.close()
				# currLine = startLine
				# # print "new File Created"

				# #update new rawADC filename to open
				# rawADCFileName = BASE_PATH+"Relay_Station{0}/rawADC/rawADC{1}.txt".format(BASE_PORT, startTimeDT)

		if iterations>=UPDATE_LENGTH:
			sumAudio = sumAudio/iterations
			iterations = 0
			audioMessage = []
			audioMessage.append("Audio")
			audioMessage.append(str("{0:.3f}".format(sumAudio))) #Energy
			audioMessage.append(str("{0:.3f}".format(sumAudioFeat))) #Teager
			tempDateTime = rNTPTime.sendUpdate(server_address, audioMessage, 5) #Audio uses startDateTime from rawADC
			sumAudio = 0
			sumAudioFeat = 0

		
	# END WHILE LOOP

# do stuff in main() -- for 'after declare' function
if __name__ == '__main__':
	main()