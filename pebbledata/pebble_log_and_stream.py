import zmq
import msgpack
from struct import unpack_from
import os
import sys
from time import sleep
import csv
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("pebble_id", type=int)
parser.add_argument("recv_port", type=str)
args = parser.parse_args()

context = zmq.Context()
# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://127.0.0.1:5000")



file_path = os.environ.get('PEBBLE_DATA_LOC')
if file_path is None:
    print("DID NOT FIND PEBBLE_DATA_LOC")
    print(os.environ)
    exit(1)

if not os.path.exists(file_path):
    os.mkdir(file_path)


newFile = True
iterFile = 0
merr = 0
print("merr = {}".format(merr))

try:
    while True:    
        data = msgpack.unpackb(receiver.recv())
        packet_count = int(len(data)/208)
        print("got {} packets".format(packet_count))
        if iterFile>=(50*60*60): newFile = True
    
        if (packet_count>0 & packet_count<10):
            timestamp = unpack_from('Q',data,208*0)
            if newFile==True:
                #datafile.close()
                filename = str(file_path) + "pebble_data_"+ str(timestamp[0]) + ".csv"
                print("file name: {}".format(filename))
                #newFile = False
                #iterFile = 0
                try:
                    with open(filename,'w') as datafile:
                        datafile.write("z,y,x,offset,timestamp\n")
                    print("Opened file: {}".format(filename))
                    newFile = False
                    iterFile = 0
                    #datafile.close()
                except:
                    merr = 1
                    print("Error opening new file!")
                    #break
                    #datafile.close()
	    print("keep moving!")				
            for k in range(packet_count):
                timestamp = unpack_from('Q',data,208*k)
                acc_data = []
                for i in range(25):
                    acc_data.append(unpack_from('hhhH',data,(208*k)+(i+1)*8))
                print("timestamp:{}".format(timestamp[0]))
                print("data:{}".format(acc_data))
                for data_t in acc_data:
                    iterFile = iterFile + 1
                    try:
                        with open(filename,'a') as datafile:
                            datafile.write("{0},{1},{2},{3},{4}\n".format(data_t[0],data_t[1],data_t[2],data_t[3],timestamp[0]))
                        #print("Wrote to file: {}".format(filename))
                        #datafile.close()
                    except:
                        merr = 1
                        #datafile.close()
                        print("Error in writing data!")
                        #receiver.close()
                        print("Going out!")
                        #exit(0)
                print("Wrote all to file: {}".format(filename))
            #datafile.close()
            #if merr==1:
            #    print("Crazy world!")
            #    merr = 0
        else:
            print("Size Error!")

except:
    print("Error!")
        
print("Exit!")
receiver.close()
print("merr={}".format(merr))
if merr==1:
    merr = 0
    sys.exit()
print("merr={}".format(merr))
#exit
