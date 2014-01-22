from PIL import Image
import os, os.path
import sys, string
import numpy
import hdr
import math
import copy
try:
    import pylab
    pylab_loaded = 1
except: pylab_loaded = 0

class reinhard(hdr.HDR):

    def __init__(self, srcDir, key, white, gamma, threshold, phi, num, low, high, srange, default):
              
        pathFolder = srcDir
        '''checking if the format is accepted
        accepted formats: PPM (extentions: ppm, pgm, pbm, pnm'''

        if (pathFolder[len(pathFolder)-1]=='p'):
            if ((pathFolder[len(pathFolder)-2]=='g')|
                (pathFolder[len(pathFolder)-2]=='b')|
                (pathFolder[len(pathFolder)-2]=='n')|
                (pathFolder[len(pathFolder)-2]=='p')):
                if(pathFolder[len(pathFolder)-3]=='p'):
                    self.imgFormat = 'ppm';
                else:
                    ##throw and exception 'Incorrect format'##
                    print 'Wrong format'

        self.srcDir = srcDir
        self.image = self.getImage(self.srcDir)
        self.pixels = self.image.load()
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.luminance = self.getLuminanceFromRGB()
    
        if default:
            self.setDefault()
        else:     
            self.key = key                       #key parameter 0.18 default'''
            self.white = white                   #''''''
            self.gamma = gamma                   #'''gamma correction 1.6 default'''
            self.threshold = threshold           #'''threshold 0.05 default'''
            self.phi = phi                       #
            self.num = num                       #
            self.low = low                       #
            self.high = high                     #
            self.srange = srange
        
    def setDefault(self):
        '''sets default values'''
        self.key       = 0.18
        self.white     = 1e20                    #(i.e. use eq 3 instead of 4)
        self.gamma     = 1.6
        self.threshold = 0.05
        self.phi       = 8.0
        self.num       = 8
        self.low       = 1
        self.high      = 43
        
    def getlogAvLum(self):

        '''Log - average luminance (approximate luminance of the scene,
            used to tdetermine the key of the scene'''
        
        N = self.width * self.height
        sumTot = 0
        luminance = self.getLuminanceFromRGB()
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                sumTot = sumTot + math.log(luminance[x,y]+0.01)

        logAvLum = (1/N)*math.exp(sumTot)
        
        return logAvLum   

    def getScaledLuminance(self, logAvLum):
        
        luminance = self.getLuminanceFromRGB()        
        scaledLuminance = numpy.zeros(shape=(self.width, self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                scaledLuminance[x,y] = (self.key/logAvLum)*luminance[x,y]

        return scaledLuminance

    def lumBurnout(self, scaledLuminance, convRes1):
        
        lumBurnout = numpy.zeros(shape=(self.width, self.height))
        sm = numpy.zeros(shape=(self.width, self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                lumBurnout[x,y] = scaledLuminance[x,y]/(1+convRes1[x, y, sm[x, y]])

        return lumBurnout

    def getGaussianProfile(self):
        
        Ri= numpy.zeros(shape=(self.width, self.height, self.srange))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                for s in range(0, (self.srange - 1)):
                    Ri[x,y,s] = (1/((self.pi*self.alpha*s)^2))*math.exp(-(x^2 +y^2)/((self.alpha*s)^2))

        return Ri

    def getDynamicRange(self):

        minval = 1e20;
        maxval = -1e20;
        luminance = self.getLuminanceFromRGB()

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
        
    def transform(self):
        scaledLuminance = self.getScaledLuminance(self.getlogAvLum())
        gaussianProfile = self.getGaussianProfile()
        print("Transform")
        return self