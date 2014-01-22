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

class iCAM(hdr.HDR):

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
        self.high      = 4
    
    
    def execute(self):
        #TO-DO:
            #1. separate out luminance and construct the Gaussian Pyramid
            #   to facilitate  the next step
            #2. compute logical adaptation luminance
            #3. apply tone mapping function TM(La, (x,y))
            #4. compute final pixel luminance
            #5. re-assemble colour image by applying the scaling obtained for
            #    luminance to each of the RGB channels
            #6. Perform gamma correction to obtain values for pixel display
            
                