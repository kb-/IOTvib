# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 19:12:01 2019

@author: Olivier
"""

def filterDictByKeyStr(d, s):
    """only keep dictionary keys containing s"""
    return {k:v for (k,v) in d.items() if s in k}

def filterDictByKeysSet(d, k):
    return {x:d[x] for x in d if x in k} 

def dictKeysStrrep(d, prefix):
    """replace string part in dictionary keys"""
    r = {}
    for k in d:
        r[k.replace(prefix,"")]  = d[k]
#    print(d)
#    print(r)
    return r