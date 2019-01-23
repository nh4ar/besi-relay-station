import zmq
import msgpack
from struct import unpack_from
import os
import sys
from time import sleep
import csv
import datetime
import argparse
import math
import rNTPTime
from Constants import *


global agiType
global agiIndx
global agiStatus

agiType=0
agiIndx=0
agiStatus=False

def main():
    pixieLog()


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
            try:
                if splitLine[0] == "PebbleFolder":
                    PebbleFolder = str(splitLine[1]).rstrip()
            except:
                print "Error reading Pebble Folder"
            # try:
            #   if splitLine[0] == "Wearable":
            #       wearable_mode = str(splitLine[1]).rstrip()
            #       if wearable_mode=="Pixie":
            #           IS_PIXIE = True
            #           IS_MEMINI = False
            #       elif wearable_mode=="Memini":
            #           IS_PIXIE = False
            #           IS_MEMINI = True
            # except:
            #   print "Error finding Pebble Mode"

            # if IS_PIXIE == True:
                
    default_settings = ''
    fconfig.close()

    return BaseStation_IP2, relayStation_ID2, PebbleFolder

def calcTeagerPerEpoch(inputList,epochInSecs=30):
    #print("in function: {},{}".format(type(len(inputList)),type(epochInSecs*50)))
    #teagerList=[]
    if (len(inputList)==(epochInSecs*50)):
        teagerList=map(lambda x,y:abs(x-y),map(lambda x:x**2,inputList[1:-1]),map(lambda x,y:x*y,inputList[2:],inputList[:-2]))
        #for indx in range(1,len(inputList)-1):
        #    teagerList.append(abs((inputList[indx]**2)-(inputList[indx-1]*inputList[indx+1])))
        teagerSum = reduce(lambda x,y:(x+y)/2,teagerList)
        return teagerSum
    else:
        return 0  




# def pixieLog(startDateTime,hostIP,BASE_PORT, pebbleFolder):
def pixieLog():
    
    global agiStatus
    global agiType
    global agiIndx

    #get info from config file
    hostIP, BASE_PORT, pebbleFolder = readConfigFile()

    server_address = (hostIP, BASE_PORT)
    # startTimeDT = rNTPTime.stripDateTime(startDateTime)
    # pixieFileName = BASE_PATH+"Relay_Station{0}/Pixie/Pixie{1}.txt".format(BASE_PORT, startTimeDT)

    
    context = zmq.Context()
    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://127.0.0.1:5000")

    # file_path = "/media/card/rtest/" #os.environ.get('PEBBLE_DATA_LOC')
    file_path = "/media/card/" + pebbleFolder + "/"
    if file_path is None:
        print("DID NOT FIND PEBBLE_DATA_LOC")
        print(os.environ)
        exit(1)
    
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    newFile = True
    iterFile = 0
    fileSize_min = 60 #min
    fileSize = fileSize_min*60*50 #min * seconds * sampling_rate
    merr = 0
#    print("merr = {}".format(merr))

#    xagi = []
#    yagi = []
#    zagi = []
    magi = []
    tgr = []
    iterations = 0
    epochSecs = 10

    while True:
        try:    
            data = msgpack.unpackb(receiver.recv())
            packet_count = int(len(data)/208)
            #print("got {} packets".format(packet_count))
            if iterFile>=(fileSize): newFile = True
            
            if (packet_count>0 & packet_count<10):
                timestamp = unpack_from('Q',data,208*0)
                if newFile==True:
                    #datafile.close()
                    filename = str(file_path) + "pebble_data_"+ str(timestamp[0]) + ".csv"
#                    print("file name: {}".format(filename))
                    #newFile = False
                    #iterFile = 0
                    try:
                        with open(filename,'w') as datafile:
                            datafile.write("z,y,x,timestamp\n")
#                        print("Opened file: {}".format(filename))
                        newFile = False
                        iterFile = 0
                        #datafile.close()
                    except:
                        merr = 1
                        print("Error opening new file!")
                        #break
                        #datafile.close()
#	        print("keep moving!")				
                for k in range(packet_count):
                    timestamp = unpack_from('Q',data,208*k)
                    acc_data = []
                    for i in range(25):
                        acc_data.append(unpack_from('hhhH',data,(208*k)+(i+1)*8))
#                    print("timestamp:{}".format(timestamp[0]))
#                    print("data:{}".format(acc_data))

                   
                    for data_t in acc_data:
                        
                        ## DATA FOR AGITATION DETECTION
                        #print("calculate m")
                        zvalue,yvalue,xvalue,offset = data_t
                        mvalue = math.sqrt(xvalue**2 + yvalue**2 + zvalue**2)
                        #zagi.append(zvalue)
                        #yagi.append(yvalue)
                        #xagi.append(xvalue)
                        magi.append(mvalue/100)
                        #print("{},{},{},{}".format(xvalue,yvalue,zvalue,mvalue))                    
                    
                        # write to a file
                        iterFile = iterFile + 1
                        try:
                            with open(filename,'a') as datafile:
                                datafile.write("{0},{1},{2},{3}\n".format(data_t[0],data_t[1],data_t[2],data_t[3]+timestamp[0]))
                            #print("Wrote to file: {}".format(filename))
                            #datafile.close()
                        except:
                            merr = 1
                            #datafile.close()
                            print("Error in writing data!")
                            #receiver.close()
                            print("Going out!")
                            #exit(0)
#                    print("Wrote all to file: {}".format(filename))
            else:
                print("Size Error!")
        
            ## PROCESSING FOR AGITATION DETECTION
            #print "PROCESSING"
            if len(magi)>=(50*3):
                magiValues = magi[-50*3:]
#               print("magi = {}".format(magiValues))
                try:
#                    print str(reduce(lambda x,y:x+y,magiValues))
                    teagerValue = calcTeagerPerEpoch(magiValues,3)
                    if teagerValue>10:
                        tgr.append(teagerValue)
#                    print("teagerValue = {}".format(teagerValue))
                    magi = []
                except:
                    print("Function Error!")
                #print("teagerValue = {}".format(teagerValue))

            
            if iterations==10:
                pixieMessage = []
                pixieMessage.append("Pixie")
                if len(tgr)>=2:
                    pixieValue = reduce(lambda x,y:x+y,tgr)
                else:
                    pixieValue = teagerValue
                # print pixieValue
                pixieMessage.append(str("{0:.3f}".format(pixieValue)))

                startDateTime = rNTPTime.sendUpdate(server_address, pixieMessage, 5)     


                iterations = 0
                if pixieValue>50:
                    agiType = 1
                    agiStatus = True
                    print "Agitation Type: " + str(agiType)
                    agiMessage = []
                    agiMessage.append("Agitation")
                    agiMessage.append(str(agiType))
                    agiMessage.append(str("{0:.3f}".format(pixieValue)))


                    # startDateTime = rNTPTime.sendUpdate(server_address, agiMessage, 5)


                    tgr = []
                    pixieValue = 0
                else:
                    del tgr[:int((len(tgr)/2)+1)]
                
            else:
                iterations +=1


        except:
            print "Error!", sys.exc_info()[0]        

    print("Exit!")
    receiver.close()
    print("merr={}".format(merr))
    if merr==1:
        merr = 0
        sys.exit()
    print("merr={}".format(merr))
#exit

# do stuff in main() -- for 'after declare' function
if __name__ == '__main__':
    main()