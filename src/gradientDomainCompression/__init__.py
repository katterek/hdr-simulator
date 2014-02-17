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

    def __init__(self, srcDir, fBeta, default):
              
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
        
        if (default):
            fBeta = 0.95
        else:
            self.fBeta = fBeta

    def gaussianPyramid(self, logLuminance):
        #Computing Gaussian Pyramid + Gradient
        numPyr = round(np.log2(min([self.width,self.height])))-np.log2(32)
        
        Xkernel = [[0, 0, 0],
                   [-1, 0, 1],
                   [0, 0, 0]]

        Ykernel = [[0,1,0],
                   [0,0,0],
                   [0,-1,0]]
        
        #logLumFlat = np.reshape(logLuminance, self.width*self.height, 1)
        #xKFlat = np.reshape(Xkernel,9,1)
        #yKFlat = np.reshape(Ykernel, 9, 1)
        #XfilteredFlat = np.correlate(logLuminance, Xkernel, "same")
       # YfilteredFlat = np.correlate(logLuminance, Ykernel, "same")
        
        '''Generation of the pyramid'''
        kx=np.matrix([1,4,6,4,1])
        ky=np.matrix([[1],[4],[6],[4],[1]])
        kernel = np.zeros(shape=(5,5))
        
        sum = 0
        for x in range(0, 5):
            for y in range(0, 5):
                kernel[x][y] = kx[x]*ky[y]
                sum = kernel[x][y] + sum
                
        for x in range(0, 5):
            for y in range(0, 5):
                kernel[x][y] = kernel[x][y]/sum
        
        pyrGrad1 = np.zeros(shape=(self.width, self.height))
        pyrGrad2 = np.zeros(shape=(self.width, self.height))
        
        for x in range (0, self.width):
            for y in range(0, self.height):
                pyrGrad1[x][y] = (Xfiltered[x]/2,Yfiltered[y]/2)
                #NOT ENTIRELY SURE ABOUT THE SECOND PART IF IT'S CORRECT INDEX
                #should maybe be [0]?
                pyrGrad2[x][y] = np.sqrt(np.power(pyrGrad1[x][y][0],2)+np.power(pyrGrad1[x][y][1],2))
                flat[i] = pyrGrad2[x][y]
                i = i + 1
        
        fAlpha = 0.1*np.mean(np.reshape(pyrGrad2, self.width, self.height))
        
        tempImg = logLuminance
        
        for i in range(1,numPyr):
            tempImg=np.reshape(tempImg, self.width*self.height)
            resImg = np.convolve(tempImgflat, kernel, "same")
            tempImg = np.reshape(resImg, self.width, self.height)
            resImg = np.convolve(tempImg,kernel, "same")
            tempImg=np.imresize(resImg,50,'bilinear', 'L')
            Fx = np.correlate(tempImg, Xkernel)/(2^(i+1))
            Fy = np.correlate(tempImg, Ykernel)/(2^(i+1))
            pyrGrad1 = [pyrGrad1, (Fx/(2^(i+1)),Fy/(2^(i+1)))]
            
        return numPyr, fAlpha

    def FattalPhi(self, gradX, gradY, fAlpha):
        
        imgOut = np.zeros(self.width, self.height)
        
        for x in range(0, len(fAlpha)):
            for y in range(0, len(self.fBeta-1)):
                grad = np.sqrt(np.power(gradX[x],2)+np.power(gradY[y],2))
        
        for x in range(0, len(fAlpha)):
            for y in range(0, len(self.fBeta-1)):
                t=np.power((grad[x,y]/fAlpha),(self.fBeta-1))
        
        for i in range(0, len(t)):
        #    if(t=='Inf'):
        #        imgOut(i) = 0
        #        imgOut(i) = mean(np.reshape(imgOut, self.width*self.height, 1))
        #    else:
        #        imgOut(i) = t
            imgOut = 0
        return imgOut

    def attenuationMask(self, nP, fAlpha, pg1, pg2):
        '''Generate attenuation mask'''
        Phi_kp1 = self.FattalPhi(pg1[nP+1][0], pg1[nP+1][1], fAlpha, self.fBeta)

        for k in range (0,nP):
            [r,c] = np.size(pg1[nP-k][0])
            G2 = np.sqrt(np.power(pg1[nP-k][0],2)+np.power(pg1[nP-k][1],2))
            fAlpha = 0.1*np.mean(np.reshape(G2, np.size(G2), 1))
            Phi_k = self.FattalPhi(pg1(nP-k).fx, pg1(nP-k).fy, fAlpha, self.fBeta)
            percentage = int(r/self.width)
            
            '''WHY THE HELL IS THAT IMPORT NOT REGOGNIZED!!!!???'''
            Phi_kp1 = np.imresize(Phi_kp1,50,'bilinear', 'L')
            for x in range (0, self.width):
                for y in range(0, self.height):
                    Phi_kp1[x,y] = Phi_kp1*Phi_k

    
    def transform(self):
        
        if (self.checkColorCoordinates()==False):
            print("Can't proceed with the algorithm execution, wrong colour coordinates")
            #TO DO: convert to RGB
        else:#DOEVERYTHING
            
            luminanceChannel = self.getLuminanceFromRGB()
            logLuminance = np.log(luminanceChannel+1e-6)
            
            #compute Gaussian Pyramid and Gradient
            print(str(self.gaussianPyramid(logLuminance)))
            #generate the attenuation mask
            #calculate the divergence with backward differences
            #solve poisson equation
            divG = 0
            PoissonSolver = 0
            Ld = np.exp(PoissonSolver(divG));
            #clamp image
            for x in range(0, self.width - 1):
                for y in range(0, self.height - 1):
                    if (Ld[x,y]>1):
                        Ld[x,y]=1
                    elif (Ld[x,y]<0):
                        Ld[x,y]=0
            #change luminance (render the image)
            newLuminance = 0
            self.modifyLuminance(newLuminance)
            self.saveTemp()
    
    '''    
   def solvePoisson(self, function):
        fshape = function.shape
        n = fshape[0]*fshape[1]
        
        ##figure out reshape
        b = - np.reshape[function, n, 1]
        
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
    '''    