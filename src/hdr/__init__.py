import Image
import os, os.path
import sys, string
import numpy
from copy import copy
try:
    import pylab
    pylab_loaded = 1
except: pylab_loaded = 0

class HDR:

    def __init__(self, srcDir):
        '''loads all images of imgFormat from imgFolder and
        resizes by a factor resize'''
    
        pathFolder = srcDir
        #pathFolder = srcDir.lower();
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
        #self.srcDir = os.path.abspath(srcDir)
        self.image = self.getImage(self.srcDir)
        self.pixels = self.image.load()
        self.width = self.image.size[0]
        self.height = self.image.size[1]

    def getImage(self, srcDir):

        image = Image.open(srcDir)
        return image

    def saveImage(self, name, image, outDir):

        image.save(outDir, format='ppm')

    def getLuminanceFromRGB(self):

        luminance = numpy.zeros(shape = (self.width,self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                '''L = 0.27R + 0.67G + 0.2B'''
                L=0.27*self.pixels[x,y][0]+0.67*self.pixels[x,y][1]+0.06*self.pixels[x,y][2]
                luminance[x,y] = L

        return luminance