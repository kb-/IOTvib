# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 20:55:16 2019

@author: Olivier
"""
import copy
from io import BytesIO
import inspect
import base64
from matplotlib import pyplot as plt
from spectralc3 import spectral
from tools import\
    filterDictByKeyStr,\
    filterDictByKeysSet,\
    dictKeysStrrep

lines = []
ax = False

def window_demo(data, fft_settings):
    """Plot window shape, adds up to 5 plots. Returns base64 png image"""
    global ax
    fft_settings_ = copy.deepcopy(fft_settings)
    new_fft_settings = dictKeysStrrep(data["FFTsettings"], "fft-")
    winParam_ = filterDictByKeyStr(new_fft_settings, "window-")
    winParam_ = dictKeysStrrep(winParam_, "window-")
    fft_settings_.update(new_fft_settings)
    fft_settings_["winParam"].update(winParam_)  #update initial window parameters with new
    #keep required parameters
    fft_settings_ = filterDictByKeysSet(fft_settings_, inspect.signature(spectral).parameters)
    sp = spectral(**fft_settings_)
    w1 = sp.w

    if not ax:
        _, ax = plt.subplots()

    if len(lines) >= 5:#limit to 5 curves
        lines.pop(0)[0].remove()
        # recompute the ax.dataLim
        ax.relim()
        # update ax.viewLim using the new dataLim
        ax.autoscale_view()
        plt.draw()
    #legend: window + winparam if exist
    lines.append(ax.plot(w1, lw=0.5, label=fft_settings_['win']+('' if  winParam_ == {} else str(winParam_))))
    ax.legend(prop={'size': 8})

    #Matplotlib to base64 picture https://stackoverflow.com/questions/31492525/converting-matplotlib-png-to-base64-for-viewing-in-html-template
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file

    figdata_png = base64.b64encode(figfile.getvalue())
#    base64_string = base64_bytes.decode(figdata_png)

    return figdata_png.decode('utf8')
