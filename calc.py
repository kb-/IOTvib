# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 21:54:42 2019

@author: Olivier
"""
from math import sqrt

def rms(num):
	return sqrt(sum(n*n for n in num)/len(num))