from PIL import Image
import os, os.path
import sys, string
import numpy
import hdr
import math
from copy import copy
try:
    import pylab
    pylab_loaded = 1
except: pylab_loaded = 0

class ToneReproduction:

    def __init__(self, key, white, gamma, threshold, phi, num, low, high, hdrImage, srange):

        self.key = key                       #key parameter 0.18 default
        self.white = white                   #
        self.gamma = gamma                   #gamma correction 1.6 default
        self.threshold = threshold           #threshold 0.05 default
        self.phi = phi                       #
        self.num = num                       #
        self.low = low                       #
        self.high = high                     #
        self.hdrImage = hdrImage             #
        self.width = self.hdrImage.width     #
        self.height = self.hdrImage.height   #
        self.luminance = self.hdrImage.getLuminanceFromRGB()
        self.srange = srange
        
    
    def logAvLum(self):

        '''Log - average luminance (approximate luminance of the scene,
            used to tdetermine the key of the scene'''
        
        N = self.width * self.height
        sumTot = 0

        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                sumTot = sumTot + math.log(self.luminance[x,y]+0.01)

        logAvLum = (1/N)*exp(sumTot)
        
        return logAvLum   

    def scaledLuminance(self, logAvLum):
        
        scaledLuminance = numpy.zeros(shape=(self.width, self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                scaledLuminance[x,y] = (self.key/logAvLum)*self.luminance[x,y]

        return scaledLuminance

    def lumBurnout(self, scaledLuminance, convRes1):
        
        lumBurnout = numpy.zeros(shape=(self.width, self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                lumBurnout[x,y] = scaledLuminance[x,y]/(1+convRes1[x, y, sm[x, y]])

        return lumBurnout

    def gaussianProfile(self):
        
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                for s in range(0, (self.srange - 1)):
                    Ri[x,y,s] = (1/((pi*alpha*s)^2))*exp(-(x^2 +y^2)/((alpha*s)^2))

        return Ri

    def dynamicRange(self):

        minval = 1e20;
        maxval = -1e20;

        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                if ((luminance[x,y]<minval) & (luminance[x,y]>0.0)):
                    minval = luminance[x,y]
                if(luminance[x,y]>maxval):
                    maxval = luminance[x,y]

        return (minval, maxval), (minval/maxval)

    def midtoneScaling(self, logAvLum):

        lowTone = self.key/3
        scaleFactor = 1/logAvLum