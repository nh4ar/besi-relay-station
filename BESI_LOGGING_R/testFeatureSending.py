from Constants import *
from socket import AF_INET, SOCK_DGRAM
import socket
import time
import sys
import os
import struct

global disconnFlag
disconnFlag = True

def sendFeature(server_address, message, timeout=5):

	global disconnFlag
	updateSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	updateSock.settimeout(timeout)

	try:
		updateSock.connect(server_address)
		if disconnFlag:
			#updateSock.sendall("Connection Up!")
			# print "Connection Up!"
			# updateSock.sendall(";".join(message))
			updateSock.sendall(message)
			disconnFlag = False
		else:
			# updateSock.sendall(";".join(message))
			updateSock.sendall(message)
			# print "Sent " + message
				
	except Exception as err:
		print "Error sending features: " + str(err)
		disconnFlag = True
	return


# testing sending
# configFileName = r'/root/besi-relay-station/BESI_LOGGING_R/config'
# fconfig = open(configFileName)
# for line in fconfig:
# 	if line[0] == "#":
# 		pass
# 	else:
# 		splitLine = line.split("=")
# 		try:
# 			if splitLine[0] == "BaseStation_IP":
# 				BaseStation_IP2 = str(splitLine[1]).rstrip()
# 		except:
# 			print "Error reading IP Address"
		
# 		try:
# 			if splitLine[0] == "relayStation_ID":
# 				relayStation_ID2 = int(splitLine[1])
# 		except:
# 			print "Error reading Port" 

# fconfig.close()
# baseFolder = BASE_PATH+"Relay_Station{}/".format(relayStation_ID2)
# hostIP = BaseStation_IP2
# BASE_PORT = 9000 

# server_address = (hostIP, BASE_PORT)

# while True:
# 	message = []
# 	message.append("z")
# 	message.append("y")
# 	message.append("x")
# 	message.append("time")

# 	sendFeature(server_address, message, 5)

# 	time.sleep(2)





