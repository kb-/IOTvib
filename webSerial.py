# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
not ok
"""

import numpy as np
import time
import threading
import copy
from serial.tools import list_ports
import serial
import struct
import matplotlib.pyplot as plt

class webSerial:
    def __init__(self):
        self.ser=None
        self.data=bytearray()
        self.thread=None
        self.sem=threading.Lock()
         
    def listPorts(self):
        #get ports with the correct VID/PID
        x=(list(list_ports.comports()))
        y=[]
        for i in x:
            if i[2].find('1B4F:8D21')!=-1:#TO DO:create listIDs and setIDvariable functions
                y.append(i[0])
        return y
    
    def getData(self):
        self.sem.acquire()
        y=copy.deepcopy(self.data)
        self.sem.release()
        
        x=np.transpose(self.parseBinary(y))
        return x
    
    def open(self,port):
        self.close()
        self.ser=serial.Serial(port,500000,timeout=1);
        
      
    #binary data is
    # unit8_t s = 0XAA;  // sync
    # uint8_t len = packet length
    # xxx bytes of packet
    #
    #  currently packet format is 
#       int32_t microSecs;  //initial testing with control loop ticks
#       int32_t desiredLoc; //65537 ticks per 360 degrees
#       int32_t actualLoc;  //65537 ticks per 360 degrees
#       int32_t angle;  //65537 ticks per 360 degrees
#       int32_t ma;

    def parseBinary(self,dataBytes):
        i=0;
        sync=False
        packLen=50;
        if (len(dataBytes)<28):
            return
        while(sync == False and i<(len(dataBytes)-packLen)):
            c=dataBytes[i:(i+packLen)]
            #print i, c
            #print ''.join('{:02x}'.format(x) for x in c)
            if (dataBytes[i]==0XAA):
                packLen=dataBytes[i+1];
                #print "packelen "
                #print packLen
                if (packLen<80):
                    x=dataBytes[i+packLen+2]
                    #print "%02X" % x
                    if (x==0XAA):
                        #print "Synced"
                        sync=True;
                        i=i+1;
            i=i+1;
        ret=[];
        while(i<(len(dataBytes)-(packLen+2))):
            c=dataBytes[i:(i+(packLen+2))]
            #print ''.join('{:02x}'.format(x) for x in c)
            i=i+packLen+2;
            fmt="<%dibb" % (packLen/4)
            #print fmt
            x=struct.unpack_from(fmt,c)
            #print x
            ret.append(x[0:(packLen/4)])
        #print ret
        return ret;
        
        
    def sendCommand(self, command):
        if (self.ser is None):
            return None
        
        s=command.rstrip('\n\r') +"\n\r"
        print("sending ", s)
        self.ser.write(s);
        
    def readData(self,event,N):
        print("running thread")
        sync=False;
        
        self.ser.flush();
#         #wait for sync bytes
#         while(sync == False):
#             c=bytearray(self.ser.read(1))[0]; 
#             if (c==0xAA):
#                 print "sync found"
#                 c=self.ser.read(13); 
#                 c=bytearray(self.ser.read(1))[0]; 
#                 if (c==0xAA):
#                     sync=True
#         
#             
#         print "synced"
        
        i=0;
        last=0;
        d=[]
        while not event.isSet():
            if (self.ser.inWaiting()>1000):
                print(self.ser.inWaiting())
            c=bytearray(self.ser.read( 2400)); 
            #s=bytearray(self.ser.read(1))[0]; 
            #print ''.join('{:02x}'.format(x) for x in c)
            #for i in range(1):
            #x=struct.unpack_from('iiibb',c)
            #d.append(copy.deepcopy(x[0:3]))
                
            self.sem.acquire()
            self.data=self.data+c
            #print len(self.data)
            #print self.data
            if (len(self.data)>N):
                self.data=self.data[-N:]
            self.sem.release()
#                  
        
    def close(self):
        if (self.ser is not None):
            self.ser.close()
            self.ser=None      
        
    def isOpen(self):
        return self.ser != None
    
    
if __name__ == '__main__':
    
    
    s=webSerial()
    s.open('com9')
    time.sleep(0.5)
    while (1):
        x=s.getData()
        print(x)
    #time.sleep(120)