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

class durandAndDorsey(hdr.HDR):

    def __init__(self, srcDir, key, lda, cmax, default):
              
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
            self.lda = lda
            self.cmax = cmax
        
    def setDefault(self):
        '''sets default values'''
        self.lda = 80
        self.cmax = 100
    
    
    def transform(self):
        #TO-DO:
        if (self.checkColorCoordinates()==False):
            print("Can't proceed with the algorithm execution, wrong colour coordinates")
            #TO DO: convert to RGB
        else:#DOEVERYTHING
            
            lumChan = self.getLuminanceFromRGB()
            #what is that??
            col = np.size(img,3);

            #Chroma
            for i in range(1,col):
                img(:,:,i) = RemoveSpecials(img(:,:,i)./lumChan)

            #Fine details and base separation
            [Lbase,Ldetail]=self.BilateralSeparation(lumChan)
            
            #tumblin-rushmeier TMO here
            
            for i in range(1, col):
                img(:,:,i)=img(:,:,i).*Lbase;


            imgOut = self.TumblinRushmeierTMO(self.img, self.Lda, self.CMax)

            #Adding details back
            for i in range(1, col)
                imgOut(:,:,i) = imgOut(:,:,i).*Ldetail
            

            #Edge-preserving filter
            #Edge-preserving as a robust statistical estimation
            #Acceleration!
                #Piecewise-linear bilateral filtering
                #subsampling
                    '''FastBilateral(Image I, spatialKernel fthethas, intensityInfluence gthethar, 
                    downsamplingFactor z)
                        J = 0 /*set the fullscale output to zero*/
                        I' = downsample(I, z)
                        f'thethas/z = downsample(fthethas, z)
                        for j = 0:NB_SEGMENTS
                            i^j = min(I) +jx(max(I) - min(I))/NB_SEGMENTS
                            G'^j  = G'j(x)f'thethas/z /*normalization factor*/
                            H'^j = G'j(x)I'  /*compute H for each pixel*/
                            H'^*j = H'j(x)f'thethas/z
                            J'^j = H'^*j/k'^j   /*normalize*/
                            J^j = upsample(J'^j, z)
                            J = J + J^j x InterpolationWeight(I, id)
                    '''
                #Contrast Reduction
                