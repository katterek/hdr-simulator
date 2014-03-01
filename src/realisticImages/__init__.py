import os, os.path
import sys, string
import numpy as np
import hdr

class tumblinAndRushmeier(hdr.HDR):

    def __init__(self, srcDir, Lda, LdMax, CMax, Lwa, default):
              
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
    
        if default:
            self.setDefault()
            
        else:
            '''adaptation display luminance in [10,30] cd/m^2'''
            self.lda = Lda
            '''maximum display luminance in [80-180] cd/m^2'''
            self.ldmax = LdMax
            '''maximum LDR monitor contrast typically between 30 to 100'''
            self.cmax = CMax
        '''adaptation world luminance cd/m^2'''
        self.lwa = np.exp(np.mean(np.reshape(np.log(self.luminance+2.3*1e-5), self.width*self.height, 1)))

    def setDefault(self):
        '''sets default values'''
        self.lda = 20
        self.cmax = 100
        self.ldmax = 100
    
    def gammaTumRushTMO(self, x):
        
        val=2.655
        if (x<=100):
            val=1.855+0.4*np.log10(x+2.3*1e-5)
        return val
        
    def transform(self):
        
        '''Range compression'''
        gamma_w = self.gammaTumRushTMO(self.lwa)
        gamma_d = self.gammaTumRushTMO(self.lda)
        
        gamma_wd = gamma_w/(1.855+0.4*np.log(self.lda))
        
        mLwa = np.zeros(shape=(self.width, self.height))
        
        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                mLwa[x,y] = np.power(np.sqrt(self.cmax),(gamma_wd-1))
        
        Ld = np.zeros(shape=(self.width, self.height))
        
        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                Ld[x,y]= self.lda*mLwa[x,y]*(np.power((self.luminance[x,y]/self.lwa),(gamma_w/gamma_d)))
                
        self.appendLog("Modifying luminance...")
        self.modifyLuminance(Ld)
        print("Image Transformed.")
        return self
