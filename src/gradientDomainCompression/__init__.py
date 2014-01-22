from PIL import Image
import os, os.path
import sys, string
import numpy as np
import hdr
import math
import copy
try:
    import pylab
    pylab_loaded = 1
except: pylab_loaded = 0

class fattal(hdr.HDR):

    def __init__(self, srcDir, fBeta):
              
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
        
        if (fBeta == None):
            fBeta = 0.95
        else:
            self.fBeta = fBeta
    
    def solvePoisson(self, function):
        fshape = function.shape
        n = fshape[0]*fshape[1]
        
        ##figure out reshape
        b = - reshape [function, n, 1]
        flatten = np.zeros(1, n)
        i = 0
        for x in range(0, fshape[0]-1):
            for y in range(0, fshape[1]-1):
                flatten[i]=function[x,y]
                i++
        
        #Build a matrix
        fours = np.ones((1,n))
        for i in range(0,n):
            fours(i)=4*fours(i)
        
        A = np.spdiags(fours, 0, n, n)
        T = np.ones((n,1))
        O = T
        
        i=n
        while (i>=0):
            T(i) = 0
            i = i - r
        
        B = np.spdiags(-T, 1 ,n, n) + np.spdiags(-O, r, n, n)
        #get Bvert
        A = A + B + Bvert
        
        #Solve Poisson equation: Ax = b
        x =A/b
        cutoff = np.zeros((1,n))
        for i in range(0, n):
            cuttoff(i) = x(i)
            
        #figure out reshape!!!
        x = reshape [cutoff, self.width, self.height]
        return x    
        
    def gaussianPyramid(self, logLuminance):
        #Computing Gaussian Pyramid + Gradient
        numPyr  = round(numpy.log2(min([self.width,self.length])))-numpy.log2(32)
        
        Xkernel = [[0, 0, 0],
                   [-1, 0, 1],
                   [0, 0, 0]]

        Ykernel = [[0,1,0],
                   [0,0,0],
                   [0,-1,0]]
        
        Xfiltered = np.correlate(logLuminance, Xkernel)
        Yfiltered = np.correlate(logLuminance, Ykernel)
        
        flat = np.zeros(1, self.width*self.height)
        i = 0
        
        for x in range (0, self.width - 1):
            for y in range(0, self.height - 1):
                pyramidGradient[x][y] = (Xfiltered[x]/2,Yfiltered[y]/2)
                #NOT ENTIRELY SURE ABOUT THE SECOND PART IF IT'S CORRECT INDEX
                #should maybe be [0]?
                pG2[x][y] = np.sqrt(pyramidGradient[x][y][0]^2+pyramidGradient[x][y][1]^2)
                flat[i] = pG2[x][y]
                i++
                
        fAlpha = 0.1*np.mean(pG2)
            
        '''Generation of the pyramid'''
        kx=np.matrix([1,4,6,4,1])
        ky=np.matrix([[1],[4],[6],[4],[1]])
        
        sum = 0
        for x in range(0, 5):
            for y in range(0, 5):
                kernel[x][y] = kx[x]*ky[y]
                sum = kernel[x][y] + sum
                
        for x in range(0, 5):
            for y in range(0, 5):
                kernel[x][y] = kernel[x][y]/sum
                
        tempImg = logLuminance
        
        for i in range(0, numPyr - 1):
                tempImg=np.imresize(convolve(tempImg,kernel),0.5,'bilinear', 'L')
                Fx = np.correlate(tempImg, Xkernel)/(2^(i+1))
                Fy = np.correlate(tempImg, Ykernel)/(2^(i+1))
                pyramidGradient = [pyramidGradient, (Fx/(2^(i+1)),Fy/(2^(i+1)))]

            #Generate attenuation mask
    
    def execute(self):
        
        if (checkColorCoordinates==False):
            print("Can't proceed with the algorithm execution, wrong colour coordinates")
            #TO DO: convert to RGB
        else:#DOEVERYTHING
            
            luminanceChannel = self.getLuminanceFromRGB()
            logLuminance = log(luminanceChannel+1e-6)
            
            #compute Gaussian Pyramid and Gradient
            #generate the attenuation mask
            #calculate the divergence with backward differences
            #solve poisson equation
            Ld = exp(PoissonSolver(divG));
            #clamp image
            for x in range(0, self.width - 1):
                for y in range(0, self.height - 1):
                    if (Ld[x,y]>1):
                        Ld[x,y]=1
                    elif (Ld[x,y]<0):
                        Ld[x,y]=0
            #change luminance (render the image)
            self.modifyLuminance(newLuminance)
            self.saveTemp()

    