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

    def getImage(self, srcDir):

        image = Image.open(srcDir)
        return image

    def saveTemp(self):
        tempDir = os.environ['HDR']
        tempDir = tempDir + '/hdr'
        self.image.save(tempDir+'/temp.ppm')
        return tempDir+'/temp.ppm'
    
    def saveImage(self, path):
        self.image.save(path)
        
    def getLuminanceFromRGB(self):

        luminance = numpy.zeros(shape = (self.width,self.height))
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                '''L = 0.27R + 0.67G + 0.2B'''
                L=0.27*self.pixels[x,y][0]+0.67*self.pixels[x,y][1]+0.06*self.pixels[x,y][2]
                luminance[x,y] = L

        return luminance
    
    def checkColorCoordinates(self):
        colourspace = self.image.getbands()
        if (colourspace != ('R', 'G', 'B')):
            print("Colour coordinates of the image should be in RGB colourspace.")
            return False
        return True
    
    def modifyLuminance(self, newLuminance):
        
        for x in range(0, (self.width - 1)):
            for y in range(0, (self.height - 1)):
                '''L = 0.27R + 0.67G + 0.2B'''
                self.pixels[x,y][0] = self.pixels[x,y][0]*(newLuminance[x,y]/self.luminance[x,y])
                self.pixels[x,y][1] = self.pixels[x,y][1]*(newLuminance[x,y]/self.luminance[x,y])
                self.pixels[x,y][2] = self.pixels[x,y][2]*(newLuminance[x,y]/self.luminance[x,y])     
        
        