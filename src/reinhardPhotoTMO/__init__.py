from PIL import Image
import os, os.path
import sys, string
import numpy as np
import hdr
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
        self.log = ""
    
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
        self.key       = 0.36
        self.white     = 1e20                    #(i.e. use eq 3 instead of 4)
        self.gamma     = 1.6
        self.threshold = 0.05
        self.phi       = 8.0
        self.num       = 8
        self.low       = 1
        self.high      = 43
        self.srange    = 2                      #size of the filter in pixels
        
    def getlogAvLum(self):

        '''Log - average luminance (approximate luminance of the scene,
            used to tdetermine the key of the scene'''
        
        N = self.width * self.height
        sumTot = 0
        luminance = self.getLuminanceFromRGB()
        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                sumTot = sumTot + np.log(luminance[x,y]+0.01)

        logAvLum = np.exp(sumTot/N)
        self.appendLog("logAvLum: " + str(logAvLum))
        return logAvLum

    def getScaledLuminance(self, logAvLum):
        
        #self.convertToFloat()        
        luminance = self.getLuminanceFromRGB()
        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                luminance[x,y] = (self.key/logAvLum)*luminance[x,y]
                self.appendLog("ScaledLuminance["+str(x)+"," +str(y)+ "]: " + str(luminance[x,y]))
        return luminance

    def lumBurnout(self, scaledLuminance, convRes1, sm):
        
        lumBurnout = np.zeros(shape=(self.width, self.height))
        #sm = np.zeros(shape=(self.width, self.height))
        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                lumBurnout[x,y] = scaledLuminance[x,y]/(1+convRes1[x, y, sm[x, y]])

        return lumBurnout

    def getGaussianProfile(self, s, alpha):
        
        '''creating a mesh of size 2*s*2+1
        twice the size of s range + 1 for the origin'''
        xs = np.linspace(-s*2, s*2, s*2*2+1)
        ys = np.linspace(-s*2, s*2, s*2*2+1)
        vx, vy = np.meshgrid(xs, ys)
        
        Ri = np.zeros(shape=(s*2*2+1, s*2*2+1))
        for x in range(0, s*2*2+1):
            for y in range(0, s*2*2+1):
                Ri[x,y] = np.exp(-(np.power(vx[x,y],2) + np.power(vy[x,y],2)))/(np.power(alpha*s,2))/(np.power(np.pi*alpha*s,2))                     
        return Ri
    
    def getLocalContrast(self, luminance):
        
        alpha1 = 1/(2*np.sqrt(2))
        alpha2 = alpha1*1.6
            
        Vs = np.zeros(shape=(self.srange, self.width, self.height))
        Vis = np.zeros(shape=(self.srange, self.width, self.height))
        V1s = np.zeros(shape=(self.width, self.height))
        V2s = np.zeros(shape=(self.width, self.height))
        
        for s in range(1, self.srange):
            Rs1 = self.getGaussianProfile(s, alpha1)
            #convolution of V = L(x,y,s)
            #correlation takes only 1d arrays
            Rs1 = np.reshape(Rs1, len(Rs1)*len(Rs1[0]))
            luminance=np.reshape(luminance, self.width*self.height)
            V1sflat = np.correlate(luminance,Rs1, "same") #center
            #restructure V1s in 2D
            a=0
            b=0
            for i in range(0, len(V1sflat)):
                #print(x,y,i)
                if (a==self.width):
                    a = 0
                    b=b+1
                V1s[a,b] = V1sflat[i]
                a=a+1
            
            ##'replicate' in MATLAB?
            Rs2 = self.getGaussianProfile(s, alpha2)
            Rs2 = np.reshape(Rs2, len(Rs2)*len(Rs2[0]))
            V2sflat = np.correlate(luminance,Rs2, "same") #surround
            #restructure V2s in 2D
            a=0
            b=0
                        
            for j in range(0, len(V1sflat)):
                if (a==self.width):
                    a = 0
                    b=b+1
                V2s[a,b] = V2sflat[i]
                a=a+1
            
            for x in range(0, (self.width)):
                for y in range(0, (self.height)):
                    self.appendLog("Vs[s,x,y] = ("+ str(V1s[x,y]) + "-" + str(V2s[x,y]) + ")/( "+ str(np.power(2,self.phi*self.key)) +"/(" + str(s^2) + "+" + str(V1s[x,y])+")")
                    Vs[s,x,y] = (V1s[x,y] - V2s[x,y])/((np.power(2,self.phi*self.key))/(s^2) + V1s[x,y])
                    Vis[s,x,y] = V1s[x,y]
                        
        return Vs, Vis
                                              
    def getAdaptationImage(self, luminance, V, V1):
        
        adaptationLuminance = luminance
        Vs = np.zeros(shape = (self.width, self.height))
        V1s = np.zeros(shape = (self.width, self.height))
        mask1 = np.zeros(shape = (self.width, self.height))
        mask0 = np.zeros(shape = (self.width, self.height))
        
        for s in range(0, (self.srange)):
            
            Vs = V[s]
            V1s = V1[s]
            
            '''find indices of v higher than threshold'''
            for x in range(0, (self.width)):
                for y in range(0, (self.height)):
                    if (Vs[x,y]>self.threshold*luminance[x,y]):
                        '''TO-CHECK:
                        is it a condition on a single pixel on indx[x,y]
                        or a condition for the whole s in the range?
                        in other words do such index higher than threshold
                        simply needs to exist to transform the masks
                        or do we actually use it to render the image?'''
                        '''don't really understand that statement'''
                        adaptationLuminance[x,y] = luminance[x,y]/(1+Vs[x,y])
                        '''let's check what that gives otherwise back to 
                        the reference material'''
                        
                '''If the difference between the pixels for given s range for local contrast
                exceeds the threshold change the value, otherwise keep it'''
                
            '''after checking all the values returned modified luminance'''
            return adaptationLuminance

    def getCompressedRange(self,scaledLuminance, adaptationLuminance, maxLuminance):
        
        compressedLuminance = np.zeros(shape = (self.width, self.height))
        
        for x in range(0, (self.width)):
                for y in range(0, (self.height)):
            
                    compressedLuminance[x,y] = (scaledLuminance[x,y]*(1+scaledLuminance[x,y]/np.power(maxLuminance,2))/(1+adaptationLuminance[x,y]))
        
        return compressedLuminance
     
    def getDynamicRange(self):

        minval = 1e20;
        maxval = -1e20;
        luminance = self.getLuminanceFromRGB()

        for x in range(0, (self.width)):
            for y in range(0, (self.height)):
                if ((luminance[x,y]<minval) & (luminance[x,y]>0.0)):
                    minval = luminance[x,y]
                if(luminance[x,y]>maxval):
                    maxval = luminance[x,y]

        return minval, maxval, (minval/maxval)

    def midtoneScaling(self, logAvLum):

        lowTone = self.key/3
        scaleFactor = 1/logAvLum
        
    def transform(self):
        if (self.checkColorCoordinates()==False):
            print("Can't proceed with the algorithm execution, wrong colour coordinates")
            self.appendLog("Can't proceed with the algorithm execution, wrong colour coordinates")
            #TO DO: convert to RGB
        else:#DOEVERYTHING
            '''get dynamic range values'''
            minval, maxval, dRange = self.getDynamicRange()
            '''Logarithmic mean calculation'''
            logAvLum = self.getlogAvLum()
            print("Average luminance obtained.")
            self.appendLog("Average luminance obtained.")
            '''Luminance Scaling with Alpha and Average Logarithimic Luminance'''
            scaledLuminance = self.getScaledLuminance(logAvLum)
            print("Luminance scaled...")
            self.appendLog("Luminance scaled...")
            '''local contrast calculation'''
            Vs, V1 = self.getLocalContrast(scaledLuminance)
            print("Local contrast obtained.")
            self.appendLog("Local contrast obtained.")
            print("Calculating adaptation luminance...")
            self.appendLog("Calculating adaptation luminance...")
            adaptationLuminance = self.getAdaptationImage(scaledLuminance, Vs, V1)           
            '''Range compression'''
            print("Range compression.")
            self.appendLog("Range compression.")
            finalLuminance = self.getCompressedRange(scaledLuminance, adaptationLuminance, maxval)
            '''Changing luminance'''
            print("Modifying luminance...")
            self.appendLog("Modifying luminance...")
            self.modifyLuminance(finalLuminance)
            #self.modifyLuminance(self.getLuminanceFromRGB())            
            print("Image Transformed.")
            self.appendLog("Image Transformed.")
            self.saveLog()
            return self