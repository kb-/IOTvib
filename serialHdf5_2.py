#import numpy as np
import time
import threading
#import datetime
#from itertools import imap
#import os
import copy
#from serial.tools import list_ports
import struct
import serial
#import ctypes
#import matplotlib.pyplot as plt
import pandas as pd

class SmartStepper:
    def __init__(self):
        self.ser = None
        self.data = bytearray()
        self.thread = None
        self.sem = threading.Lock()
        #TO DO: set as default, but allow to define at init time
        self.fmt = "<BBIIhhhH"
        self.l_packet = 320
        self.l_fmt = struct.calcsize(self.fmt)
        self.sync = False
        self.df = pd.DataFrame(columns=('break', 'len', 't', 'n', 'x', 'y', 'z', 'i'))

    def getData(self):
        self.sem.acquire()
        y = copy.deepcopy(self.data)
        self.sem.release()
        self.parseBinary(y)
        return self.df

    def open(self, port):
        self.close()
        self.ser = serial.Serial(port, 500000, timeout=1)
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

    def parseBinary(self, dataBytes):
        # while self.sync and (i<(len(dataBytes)-(self.l_fmt))):
        if self.sync:
            for i in range(self.l_packet-1):
                tup = struct.unpack_from(self.fmt, dataBytes[i*self.l_fmt:(i+1)*self.l_fmt])
                # print(x)
                self.df.loc[self.df.index.max() + 1] = tup

    def sync_data(self, bs):
        for i in range(self.l_fmt):
            #1st sync byte & second sync byte & data length (fmt-sync-length byte)
            if bs[i] == 0XAA & bs[i+self.l_fmt] == 0XAA & bs[i+1] == self.l_fmt-2:
                return i
        return -1

    def startData(self):
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.readData, args=(self.event, 500000, ))
        self.thread.daemon = True
        self.thread.start()
        self.running = True

    def readData(self, event, N):
        print("running thread")
        self.ser.flush()

        while not event.isSet():
            if self.ser.inWaiting() > 1000:
                print(self.ser.inWaiting())
            if not self.sync:
                lag = self.sync_data(self.ser.read(self.l_fmt*2))
                print(lag)
                self.ser.read(lag)#discard out ofsync data
    
                 #check sync
                  #       b=s.read(36)
                  #       lag = sync_data(b)
                  #       print(lag)
                self.sync = True
            if self.sync == True:
                c = self.ser.read(self.l_packet*self.l_fmt)#read up to 2400 bytes
                self.sem.acquire()
                self.data = self.data+c
                #print(len(self.data))
                #print(self.data)
                if len(self.data) > N:
                    self.data = self.data[-N:]
                self.sem.release()

    def stopData(self):
        self.event.set()

    def close(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None

    def isOpen(self):
        return self.ser != None

if __name__ == '__main__':
    s = SmartStepper()
    s.open('com9')
    time.sleep(0.5)
    s.startData()
    time.sleep(0.1)
    time.sleep(1)
    # plt.ion()
    # fig=plt.figure()
    # ax=fig.add_subplot(2,1,1)
    # p,=ax.plot([],[],label='Encoder');
    # plt.grid(True)
    # plt.hold(True)
    # p2,=ax.plot([],[],label='Electrical');
    # p3,=ax.plot([],[],label='Desired');
    # ax.set_autoscaley_on(True)
    # ax.legend()
    # plt.ylabel('Deg')

    # ax2=fig.add_subplot(2,1,2)
    # l,=ax2.plot([],[]);
    # plt.ylabel('mA')
    # ax2.grid(True)

#     x=s.getData();
#     print(len(x[0]))
#     plt.plot(x[0],x[1])
#     plt.show();
#     exit()

#    plt.axis([0, 10, 0, 1])

    while 1:
        x = s.getData()
        if x is not None:
            if len(x) > 0:
                1
#                print(x)
                # t=np.subtract(x[0],x[0][0])
                # t=t/1.0e6

                # des=np.mod(np.multiply(x[1],360.0/65536.0),360)
                # e=np.mod(np.multiply(x[2],360.0/65536.0),360)
                # elec=np.mod(np.multiply(x[3],360.0/65536.0),360)     
# #                 ix=np.where(des>180)
# #                 des[ix]=des[ix]-360
# #
# #                 ix=np.where(e>180)
# #                 e[ix]=e[ix]-360
# #
# #                 ix=np.where(elec>180)
# #                 elec[ix]=elec[ix]-360
                # #print(len(t), len(x[2]))
                # p.set_xdata(t)
                # p.set_ydata(e)
                # p2.set_xdata(t)
                # p2.set_ydata(elec)
                # p3.set_xdata(t)
                # p3.set_ydata(des)
                # l.set_xdata(t)
                # l.set_ydata(x[4])
                # ax.relim()
                # ax.autoscale_view()
                # ax2.relim()
                # ax2.autoscale_view()
                # fig.canvas.draw()
                # plt.pause(.1)
    # time.sleep(120)
    # s.stopData()
