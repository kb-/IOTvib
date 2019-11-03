# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 02:08:03 2019

@author: Olivier
"""

import serial

ser = serial.Serial('COM9',500000)
read_byte = ser.read()
x = []
while read_byte is not None:
    read_byte = ser.read(8)
    x+=read_byte