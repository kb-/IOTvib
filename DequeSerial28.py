'''Read accelerometer data from Arduino, stream data and FFT to websocket'''
# -*- coding: utf-8 -*-
#
# get binary data from Arduino, transfer binary data to browser + 3 fft tracks,
# save data, control 2 way socket, start/pause, record data on/off
# ok with WSbrowser35 :)

import threading
import struct
import json
import time
import collections
#from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools
import os
import shutil
import inspect
import copy
import serial
#import datetime
#import random
import websockets

from spectralc3 import spectral
from plotfigure import window_demo
from tools import\
    filterDictByKeysSet,\
    filterDictByKeyStr,\
    dictKeysStrrep

import numpy as np
import h5py
#import traceback, sys, code
#import struct

# Arduino serial settings
port = 'COM9'
baud = 500000               # read fast! don't lose too much CPU cycles reading

# sensor data
fs = 1600                    # ADXL345: 1600 Hz (bad signal at 3200 Hz) demo 800
l_packet = int(fs / 10)     # 0.1 s of data

ntracks = 3

fmt = "<bIIhhhHb"   # incoming data format:
                    # sync byte, size byte, time uint32, count uint 32, xyz int16, spare uint16

fmt2 = "<fff"       # outgoing FFT data format

l_fmt = struct.calcsize(fmt)

l_fmt2 = struct.calcsize(fmt2)

paused = True

#cnt = 0
buffer = collections.deque()    # read/outgoing data buffer
buffer2 = collections.deque()   # spectrum outgoing data buffer

df = 2                          # FFT resolution (s)
overlap = 0.75                  # FFT block overlap (0 <= overlap <1; 0 = no overlap)
fftwindow = 'hann'
fftaveraging = 'exp'
nAverage = 10
                                        # TO DO: test all FFT settings

fftlines = fs / df
fft_settings = {"fs": fs, "nlines": fftlines, "overlap": overlap, "win": fftwindow,
                "averaging": fftaveraging, "nAverage": nAverage,
                "winParam": {"sym": False}, "detrend": "constant"}
new_fft_settings = copy.deepcopy(fft_settings)
# open serial connection with Arduno
try:
    ser = serial.Serial(port, baud, timeout=1)
except serial.SerialException:
    ser.close()
    raise


def setSpectrum(new_settings):
    """Initialize spectrum calculation"""
    global new_fft_settings
    fft_settings_ = copy.deepcopy(fft_settings)
    fft_settings_.update(new_settings)
    # remove unrequired keys
    fft_settings_ = filterDictByKeysSet(fft_settings_, inspect.signature(
        spectral).parameters)  # keep required parameters
    print("fft_settings_", fft_settings_)
#    import pdb; pdb.set_trace()
    new_fft_settings = fft_settings_
    sp = []
    for _ in range(ntracks):
        sp.append(spectral(**fft_settings_))
    return sp


spectrum = setSpectrum({})


def setSettings():
    """"Set settings structure"""
    return {
        "record_data": True,
        "record_fft": False,
        "fs": fs,
        "ntracks": ntracks,
        "tracks": ["X", "Y", "Z"],
        "units": ["g", "g", "g"],
        "gain": [0.00376390, 0.00376009, 0.00349265],
        "fft": {
            "nlines": new_fft_settings["nlines"],
            "df": fs / new_fft_settings["nlines"],              # df,
            "overlap_pct": new_fft_settings["overlap"] * 100.,  # overlap*100,
            "win": new_fft_settings["win"],                  # fftwindow,
            "averaging": new_fft_settings["averaging"],         # fftaveraging,
            "nAverage": new_fft_settings["nAverage"],
            "t_step": 1. / df * (1. - new_fft_settings["overlap"]),
            "ECF": spectrum[0].getECF(),
            "detrend": new_fft_settings["detrend"]
        },

        #unit conversion table: unit, scale, integration
        "conversion": [{"u": "g", "sc": 1, "int": 0},
                       {"u": "m/s^2", "sc": 9.80665, "int": 0},
                       {"u": "m/s", "sc": 9.80665, "int": 1},
                       {"u": "mm/s", "sc": 9806.65, "int": 1},
                       {"u": "m", "sc": 9.80665, "int": 2},
                       {"u": "mm", "sc": 9806.65, "int": 2},
                       {"u": "um", "sc": 9806650, "int": 2}]
    }


settings = setSettings()

def read_from_port(s, appendData, appendData2):
    """Read data from Aduino"""
    syncB(s, s.read(l_fmt * 2))                     # sync data with 2 samples
    while True:
        if s.inWaiting() > l_fmt * l_packet:
            read_byte = s.read(l_fmt * l_packet)    # read 0.1 s of data
            if read_byte is not None:
                if not paused:
                    appendData(read_byte)           # append element to right of buffer
                    appendData2(read_byte)

        time.sleep(0.09)                            # reduce CPU load


def syncB(s, d):
    """synchronize data stream with sync bytes and packet length"""
    for i in range(l_fmt):
        # 1st sync byte & second sync byte & data length (fmt-sync and length bytes)
        if d[i] == 0XAA & d[i + l_fmt] == 0XAA & d[i + 1] == l_fmt - 2:
            break   # i at break is out of sync data length
    s.read(i)       # discard out of sync data


# websocket
start_time = time.time()
#cnt_data_sent = 0;


async def useB(websocket, _):
    """Send data in buffer to websocket"""
#    global cnt_data_sent
    while True:
        try:
            if not paused:
                data = buffer.popleft()  # pop element from left of buffer (oldest read_byte block)
                await websocket.send(data)
#                cnt_data_sent +=1
#                print("--- %s seconds ---" % ((time.time() - start_time)/cnt_data_sent))
        except IndexError:  # don't stop if first reads are empty
            continue
        finally:
            await asyncio.sleep(0.09)

x = np.zeros(l_packet)
y = np.zeros(l_packet)
z = np.zeros(l_packet)


def unpackB(b):
    """Unpack binary data"""
    cnt = 0
    for i in range(l_packet):
        d = struct.unpack_from(fmt, b[i * l_fmt:(i + 1) * l_fmt])
        x[cnt] = d[3]  # *xGain            #x axis
        y[cnt] = d[4]  # y axis
        z[cnt] = d[5]  # z axis
        cnt += 1
    return np.array([x, y, z])


def packB(d):  # d is 2d array
    """Pack to binary data"""
    b = []
    for i in range(len(d[0])):
        args = (fmt2, ) + tuple(d[:, i])
        b += struct.pack(*args)
    return bytearray(b)


spectrumReady = np.zeros(ntracks)


def cb(i):
    """Callback on FFT added to buffer"""
    global spectrumReady
    spectrumReady[i] = True

    return True


# websocket2
nline_change = False


async def useBfft(websocket, _, spec):
    """Send FFT to websocket"""
    global spectrumReady, spectrum, nline_change
    Y = np.zeros([ntracks, int(np.ceil(fftlines / 2))])
    # start_time = time.time()

    while True:
        if nline_change:
            nline_change = False
            Y = np.zeros([ntracks, int(np.ceil(fftlines / 2))])
        if not paused:
            try:
                # pop element from left of buffer (oldest read_byte block)
                spec = spectrum
                dataB = buffer2.popleft()
                if dataB is not None:
                    data = unpackB(dataB)
                    if settings["record_data"]:
                        dsts.resize((ntracks, dsts.shape[1] + l_packet))
                        dsts[:, -l_packet:] = data

                    for i in range(len(data)):          # loop on tracks
                        bound_cb = functools.partial(cb, i)
                        for j in range(len(data[i])):   # loop on samples
                            spec[i].addS(data[i, j], cb=bound_cb)
                        Y[i, :], _ = spec[i].get()
                    if np.all(spectrumReady):           # check if all done
                        spectrumReady = np.zeros(ntracks)
                        await websocket.send(packB(Y))

            except IndexError:  # don't stop if first reads are empty
                continue
        await asyncio.sleep(0.09)

    # print("--- %s seconds ---" % (time.time() - start_time))
    # print('done')


# websocket3
async def cmd(websocket, _):
    """Read commands, send current settings from/to websocket"""
    global paused, spectrum, fftlines, nline_change, settings

    #send default settings
    await websocket.send(json.dumps({"action": "settings", "settings": settings}))
    print('waiting cmd')
    async for message in websocket:
        data = json.loads(message)
        print(data)

        #pause incoming serial data processing
        if data["action"] == "pause":
            paused = True
#            ser.close()

        #start incoming serial data processing
        if data["action"] == "start":
            paused = False

        #handle incoming boolean settings
        if data["action"] == "settingsBool":
            if data["n"] == "record_data":          #activate data recording
                settings["record_data"] = data["v"]

        #change FFT settings
        if data["action"] == "settingsFFT":
            #            import pdb; pdb.set_trace()
            fft_settings_ = copy.deepcopy(fft_settings)
            new_fft_settings_ = dictKeysStrrep(data["FFTsettings"], "fft-")
            winParam_ = filterDictByKeyStr(new_fft_settings_, "window-")
            winParam_ = dictKeysStrrep(winParam_, "window-")
            fft_settings_.update(new_fft_settings_)

            # update initial window parameters with new
            fft_settings_["winParam"].update(winParam_)
#            print(fft_settings_)
            nline_change = True
            fftlines = fft_settings_["nlines"]

            # update spectrum with new settings
            spectrum = setSpectrum(fft_settings_)
            settings = setSettings()
            await websocket.send(json.dumps({"action": "settings", "settings": settings}))

        #send picture of window function, ploted over previos ones
        if data["action"] == "display_window":
            pic = window_demo(data, fft_settings)   #generate picture
            await websocket.send(json.dumps({"action": "display_window", "pic": pic}))


async def serve(port_, fn):
    """Start a websocket"""
    return await websockets.serve(fn, "127.0.0.1", port_)


async def runTogether():
    """Group function executed in Asyncio loop"""
    # pack arguments for useBff because websockets.serve doen't take extra arguments
    bound_useBfft = functools.partial(useBfft, spec=spectrum)
    await asyncio.gather(serve(5678, useB), serve(5677, bound_useBfft), serve(5676, cmd))

# create hdf5 file
if os.path.exists("file.h5"):
    shutil.copy2("file.h5", "file_old.h5")
    os.remove("file.h5")
with h5py.File('file.h5') as file:
    
    # timeseries: contains all tracks, raw int16 data (as downloaded)
    dsts = file.create_dataset('ts',
                               (ntracks, 0),
                               maxshape=(ntracks, None),
                               chunks=(ntracks, l_packet),
                               dtype='i2',
                               compression="lzf")
    dsts_cnt = 0
    
    try:
        thread = threading.Thread(target=read_from_port, args=(
            ser, buffer.append, buffer2.append))
        thread.start()
    
        loop = asyncio.get_event_loop()
        loop.run_until_complete(runTogether())
        loop.run_forever()
    
    except KeyboardInterrupt:
        ser.close()
