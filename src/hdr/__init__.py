import Image
import os, os.path
import sys, string
import numpy as np
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
        self.log = ""

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
    
    def convertToFloat(self):
        
        for x in range(0, self.width):
            for y in range(0, self.height):
                pixel = list(self.pixels[x,y])
                pixel[0] = float(pixel[0])
                pixel[1] = float(pixel[1])
                pixel[2] = float(pixel[2])
                
                floatPixel = tuple(pixel)
                self.pixels[x,y] = floatPixel
    
    def appendLog(self, string):
       
        self.log = self.log + "\n" + string
        
    def saveLog(self):
        
        tempDir = os.environ['HDR']
        text_file = open(tempDir + "/log.txt", "w") 
        text_file.write(self.log)
        
    def getHistogram(self):
        return self.image.histogram()
    
    def getLuminanceMode(self, histogram):
        
        mode = 0
        for x in range(0, len(histogram)):
            if (histogram[x]>mode):
                mode = x                
        
        return mode
        
    def getLuminanceFromRGB(self):

        luminance = np.zeros(shape = (self.width,self.height))
        for x in range(0, self.width):
            for y in range(0, self.height):
                '''L = 0.27R + 0.67G + 0.06B'''
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
        
        log = ""
                
        for x in range(0, self.width):
            for y in range(0, self.height):
                '''L = 0.27R + 0.67G + 0.2B'''
                pixel = list(self.pixels[x,y])
                pixel[0] = int(pixel[0]*(newLuminance[x,y]/self.luminance[x,y]))
                pixel[1] = int(pixel[1]*(newLuminance[x,y]/self.luminance[x,y]))
                pixel[2] = int(pixel[2]*(newLuminance[x,y]/self.luminance[x,y])) 
                
                log = log + "pixel[0]: " + str(pixel[0]) + " newLuminance[x,y]: " + str(newLuminance[x,y]) + " self.luminance[x,y]: " + str(self.luminance[x,y]) + "\n" +"pixel[1]: " + str(pixel[1]) + " newLuminance[x,y]: " + str(newLuminance[x,y]) + " self.luminance[x,y]: " + str(self.luminance[x,y]) + "\n" + "pixel[2]: " + str(pixel[2]) + " newLuminance[x,y]: " + str(newLuminance[x,y]) + " self.luminance[x,y]: " + str(self.luminance[x,y]) + "\n"
                
                updatedPixel = tuple(pixel)
                self.pixels[x,y] = updatedPixel
        
        self.appendLog(log)
    
    def convolve2d(self, array1, array2):
        
        width = np.shape(array1)[0]
        height = np.shape(array1)[1]
        
        fArray1 = np.reshape(array1, width*height, 1)
        fArray2 = np.reshape(array2, np.shape(array2)[0]*np.shape(array2)[1], 1)
        fconvolution = np.convolve(fArray1, fArray2, "same")
        a=0
        b=0

        convolution = np.zeros(shape=(width, height))               
        for j in range(0, len(fconvolution)):
            if (a==width):
                a = 0
                b=b+1
                convolution[a,b] = fconvolution[j]            
                a=a+1
                
        return convolution
            
    def correlate2d(self, array1, array2):
        
        width = np.shape(array1)[0]
        height = np.shape(array1)[1]
        
        fArray1 = np.reshape(array1, width*height, 1)
        fArray2 = np.reshape(array2, np.shape(array2)[0]*np.shape(array2)[1], 1)
        fcorrelation = np.correlate(fArray1, fArray2, "same")
        a=0
        b=0

        correlation = np.zeros(shape=(width, height))                  
        for j in range(0, len(fcorrelation)):
            if (a==width):
                a = 0
                b=b+1
                correlation[a,b] = fcorrelation[j]            
                a=a+1
                
        return correlation
            
        