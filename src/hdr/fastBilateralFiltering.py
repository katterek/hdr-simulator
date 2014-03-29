from PIL import Image
import os, os.path
import sys, string
import numpy as np
from scipy import interpolate
from scipy import ndimage
import hdr
import realisticImages

class durandAndDorsey(hdr.HDR):

    def __init__(self, srcDir, lda, cmax, default):
              
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
        self.log = ""
        if default:
            self.setDefault()
        else:     
            self.lda = lda
            self.cmax = cmax
        
    def setDefault(self):
        '''sets default values'''
        self.lda = 80
        self.cmax = 100
    
    '''def bilateralFilter(self, data, edge, edgeMin, edgeMax,sigmaSpatial, sigmaRange,samplingSpatial, samplingRange):
    try:
            
        except LowerThan2:
            
        if( ndims( data ) > 2 ):
            error( 'data must be a greyscale image with size [ height, width ]' )
    
        if( ~isa( data, 'double' ) ),
            error( 'data must be of class "double"' );
    end
    
    if ~exist( 'edge', 'var' ),
        edge = data;
    elseif isempty( edge ),
        edge = data;
    end
    
    if( ndims( edge ) > 2 ),
        error( 'edge must be a greyscale image with size [ height, width ]' );
    end
    
    if( ~isa( edge, 'double' ) ),
        error( 'edge must be of class "double"' );
    end
    
    inputHeight = size( data, 1 );
    inputWidth = size( data, 2 );
    
    if ~exist( 'edgeMin', 'var' ),
        edgeMin = min( edge( : ) );
        warning( 'edgeMin not set!  Defaulting to: %f\n', edgeMin );
    end
    
    if ~exist( 'edgeMax', 'var' ),
        edgeMax = max( edge( : ) );
        warning( 'edgeMax not set!  Defaulting to: %f\n', edgeMax );
    end
    
    edgeDelta = edgeMax - edgeMin;
    
    if ~exist( 'sigmaSpatial', 'var' ),
        sigmaSpatial = min( inputWidth, inputHeight ) / 16;
        fprintf( 'Using default sigmaSpatial of: %f\n', sigmaSpatial );
    end
    
    if ~exist( 'sigmaRange', 'var' ),
        sigmaRange = 0.1 * edgeDelta;
        fprintf( 'Using default sigmaRange of: %f\n', sigmaRange );
    end
    
    if ~exist( 'samplingSpatial', 'var' ),
        samplingSpatial = sigmaSpatial;
    end
    
    if ~exist( 'samplingRange', 'var' ),
        samplingRange = sigmaRange;
    end
    
    if size( data ) ~= size( edge ),
        error( 'data and edge must be of the same size' );
    end
    '''
    
    def bilateralFilter(self,luminance,sigma_d,sigma_r):
        # Pre-compute Gaussian domain weights.
        w=5
        xx = np.linspace(-w, w,(2*w+1))
        yy = np.linspace(-w, w,(2*w+1))
        X,Y = np.meshgrid(xx,yy)
        G = X
        print np.size(X)
        for x in range(0, 2*w):
            for y in range(0, 2*w):
                G[x,y] = np.exp(-(np.power(X[x,y],2)+np.power(Y[x,y],2))/(2*np.power(sigma_d,2)))

        #Rescale range variance (using maximum luminance).
        sigma_r = 100*sigma_r

        # Apply bilateral filter.
        
        Base = np.zeros(shape = (self.width, self.height))

        for x in range(0, self.width):
            for y in range(0, self.height):
                # Extract local region.
                if ((x-w)<1):
                    iMin = 1
                else:
                    iMin = x-w
                if ((x+w)>self.width):
                    iMax = self.width
                else:
                    iMax = x+w
                if ((y-w)<1):
                    jMin = 1
                else:
                    jMin = y-w
                    
                if ((y+w)>self.height):
                    jMax = self.height
                else:
                    jMax = y+w
               
                I = np.zeros(shape = (iMax-iMin,jMax-jMin))
                H = np.zeros(shape = (iMax-iMin,jMax-jMin))
                F = np.zeros(shape = (iMax-iMin,jMax-jMin))
                q = np.zeros(shape = (iMax-iMin,jMax-jMin))
                for i in range(0, (iMax-iMin)):
                    for j in range(0,(jMax-jMin)):
                        I[i,j] = luminance[i+iMin,j+jMin]
                        # Compute Gaussian range weights
                        H[i,j] =  np.exp(-np.power((I[i,j]-luminance[x,y]),2)/(2*np.power(sigma_r,2)))
                        #calculate the bilateral filter response

                        for ix in range(iMin, iMax):
                            for jy in range(jMin, jMax):
                                F[i,j] = H[i,j]*G[ix-x+w,jy-y+w]
                        q = F[i,j]*I[i,j]
                #print np.sum(q)
                #print np.sum(F)
                #print x,y
                #print Base[x,y]
                Base[x,y] = np.sum(q)/np.sum(F)
                        
        return Base
        
    def aabilateralFilter(self, data, sigmaRange, sigmaSpatial):
        
        edge = data
        
        edgeMin = np.min(edge)
        edgeMax = np.max(edge)
        
        edgeDelta = edgeMax - edgeMin
    
        samplingRange = sigmaRange
        samplingSpatial = sigmaSpatial
        print("sigmaRange", str(sigmaRange))
        print("sigmaSpatial", str(sigmaSpatial))
        print("samplingRange", str(samplingRange))
        print("samplingSpatial", str(samplingSpatial))
        print("edgeDelta", str(edgeDelta))
        
        '''parameters'''
        derivedSigmaSpatial = sigmaSpatial/samplingSpatial
        derivedSigmaRange   = sigmaRange/samplingRange
        
        print("derivedSigmaSpatial", str(derivedSigmaSpatial))
        print("derivedSigmaRange", str(derivedSigmaRange))
        paddingXY = np.floor(2*derivedSigmaSpatial) + 1
        paddingZ = np.floor(2*derivedSigmaRange) + 1
        
        #derivedSigmaSpatialFl = np.zeros(shape=(derivedSigmaSpatial))
        #derivedSigmaRangeFl = np.zeros(shape=(derivedSigmaRange))        
        
        #for i in range(0, len(derivedSigmaSpatialFl)):
            
        #    derivedSigmaSpatialFl[i] = np.floor(2*derivedSigmaSpatial[i])+1        
        
        #for i in range(0, len(derivedSigmaRange)):
            
        #    derivedSigmaRangeFl[i] = np.floor(2*derivedSigmaRange[i]) + 1
        
        '''allocate 3D grid'''
        downsampledDepth  = np.floor(edgeDelta/samplingRange) + 1 + 2 * paddingZ
        downsampledWidth  = np.floor((self.width-1) / samplingSpatial ) + 1 + 2 * paddingXY
        downsampledHeight = np.floor((self.height-1)/ samplingSpatial ) + 1 + 2 * paddingXY
        
        print(str(downsampledDepth), str(downsampledWidth), str(downsampledHeight))
    
        gridData    = np.zeros( shape =(downsampledHeight, downsampledWidth, downsampledDepth))
        gridWeights = np.zeros( shape =(downsampledHeight, downsampledWidth, downsampledDepth))
    
        '''compute downsampled indices'''
        ii=np.linspace(0, self.width-1, self.width)
        jj=np.linspace(0, self.height-1, self.height)
    
        jj,ii = np.meshgrid(jj, ii)
        
        ''' so when iterating over ii( k ), jj( k )
        get: ( 0, 0 ), ( 1, 0 ), ( 2, 0 ), ... (down columns first)'''
        
        di = np.zeros(shape=(self.width, self.height))
        dj = np.zeros(shape=(self.width, self.height))    
        
        for i in range(0, self.width):
            for j in range(0,self.height):
                di[i,j] = np.round(ii[i,j]/samplingSpatial) + paddingXY + 1
                dj[i,j] = np.round(jj[i,j]/samplingSpatial) + paddingXY + 1        
        
        dz = np.round((edge - edgeMin)/samplingRange) + paddingZ + 1
    
        '''perform scatter (there's probably a faster way than this)
        normally would do downsampledWeights( di, dj, dk ) = 1, but we have to
        perform a summation to do box downsampling'''

        for x in range(0, self.width):
            for y in range(0, self.height):
                dataZ = data[x,y]
                ''' traverses the image column wise, same as di( k )'''
                #if ~isnan(dataZ):
            
                '''solve how to treat K!!!'''
                dik = di[x,y]
                djk = dj[x,y]
                dzk = dz[x,y]
                
                gridData[dik,djk,dzk] = gridData[dik, djk, dzk] + dataZ
                gridWeights[dik, djk, dzk] = gridWeights[dik, djk, dzk] + 1
        
        '''make gaussian kernel'''
        kernelWidth  = 2 * derivedSigmaSpatial + 1
        kernelHeight = kernelWidth
        kernelDepth  = 2 * derivedSigmaRange + 1
        
        halfkernelWidth  = np.floor(kernelWidth / 2 )
        halfkernelHeight = np.floor(kernelHeight / 2 )
        halfkernelDepth  = np.floor(kernelDepth / 2 )
        
        gridX, gridY, gridZ = np.mgrid[-halfkernelWidth:halfkernelWidth+1, -halfkernelHeight:halfkernelHeight+1, -halfkernelDepth:halfkernelDepth+1]
        gridRSquared = np.zeros(shape = (kernelDepth, kernelWidth, kernelHeight))
        kernel = gridRSquared
        
        '''TO-DO:figure out indices'''
        for x in range(0, int(kernelHeight)):
            for y in range(0, int(kernelWidth)):
                for z in range(0, int(kernelDepth)):
                    gridRSquared[z,x,y] = (np.power(gridX[z,x,y],2) + np.power(gridX[z,x,y],2))/(np.power(derivedSigmaSpatial,2))+(np.power(gridZ[z,x,y],2))/(np.power(derivedSigmaRange,2))
                    kernel[z,x,y] = np.exp(-0.5 * gridRSquared[z,x,y])
        
        '''convolve'''
        
        #blurredGridData = ndimage.convolve(gridDataFlat, kernelFlat, "same")
        #blurredGridWeights = ndimage.convolve(gridWeightsFlat, kernelFlat, "same")
        blurredGridData = ndimage.convolve(gridData, kernel, mode='constant', cval=0.0)
        blurredGridWeights = ndimage.convolve(gridWeights, kernel, mode='constant', cval=0.0)

        normalizedBlurredGrid = np.zeros(shape=(np.shape(blurredGridWeights)))
        '''divide'''
        
        for x in range(0, np.shape(blurredGridWeights)[0]):
            for y in range(0, np.shape(blurredGridWeights)[1]):
                for z in range(0, np.shape(blurredGridWeights)[2]):

                    if (blurredGridWeights[x,y,z]==0):
                        blurredGridWeights[x,y,z] = -2
                    elif (blurredGridWeights[x,y,z]<-1):
                        blurredGridWeights[x,y,z]=0
                    normalizedBlurredGrid[x,y,z] = blurredGridData[x,y,z] / blurredGridWeights[x,y,z]
        
        '''for debugging'''
        '''blurredGridWeights( blurredGridWeights < -1 ) = 0; % put zeros back'''
        
        '''upsample'''
        jj, ii = np.mgrid[ 0 : self.width, 0 : self.height ]
        
        di = np.zeros(shape=(self.width, self.height))
        dj = np.zeros(shape=(self.width, self.height))
        
        '''no rounding'''
        for x in range(0, self.width):
            for y in range(0, self.height):
                di[x,y] = (ii[x,y] / samplingSpatial ) + paddingXY + 1
                dj[x,y] = (jj[x,y] / samplingSpatial ) + paddingXY + 1
        dz = (edge - edgeMin) / samplingRange + paddingZ + 1
        
        '''interpn takes rows, then cols, etc
        i.e. size(v,1), then size(v,2), ...'''
        '''multidimentional data interpolation'''
        #output1 = interpolate.griddata( normalizedBlurredGrid, di, dj, dz )
        print(str(np.size(normalizedBlurredGrid)), str(np.size(di)), str(np.size(dj)), str(np.size(dz)))
        output = interpolate.interp1d( normalizedBlurredGrid, di,dj,dz)
        #output1 = interpolate.griddata( normalizedBlurredGrid, di,'linear')
        #output2 = interpolate.griddata( output1, dj, 'linear')
        #output3 = interpolate.griddata( output2, dz, 'linear')
                
        return output
    
    def BilateralSeparation(self,img):
        
        '''default parameters'''
       
        rangeS = 4
        spatialS = 0.5
        
        tmp = np.zeros(shape = (self.width, self.height))
        Base = np.zeros(shape = (self.width, self.height))
        Detail = np.zeros(shape = (self.width, self.height))

        for x in range(0, self.width):
            for y in range (0, self.height):
                tmp[x,y] = np.log(img[x,y]+1)        
        
        Base = self.bilateralFilter(img,rangeS,spatialS)

        '''Extracting Base and Detail Layers'''
        '''Removing 0'''
        for x in range(0,self.width):
            for y in range(0, self.height):
                if (Base[x,y]<0):
                    Base[x,y] = 0
                    Detail[x,y] = self.maxLum
                else:
                    Detail[x,y] = (img[x,y]/Base[x,y])
        
        return Base, Detail

    
    def transform(self):
        
        if (self.checkColorCoordinates()==False):
            print("Can't proceed with the algorithm execution, wrong colour coordinates")
            #TO DO: convert to RGB
        else:
            
            lumChan = self.getLuminanceFromRGB()
            #img(:,:,i) = RemoveSpecials(img(:,:,i)./lumChan)

            '''Fine details and base separation'''
            Lbase,Ldetail=self.BilateralSeparation(lumChan)
            
            '''tumblin-rushmeier TMO here'''
            

            for x in range(0,self.width):
                for y in range(0,self.height):
                    lumChan[x,y]=lumChan[x,y]*Lbase[x,y]
            
            '''save img into a temporary location'''
            self.luminance = lumChan            
            tempFile = self.saveTemp()
            
            Lda = 0
            LdMax = 0
            CMax = 0            
            
            image = realisticImages.tumblinAndRushmeier(tempFile, Lda, LdMax,CMax, 1)
            tumblinImage = image.transform()
            tempFile = tumblinImage.saveTemp()
            
            '''Update image properties from the temporary file'''
            self.srcDir = tempFile
            self.image = self.getImage(self.srcDir)
            self.pixels = self.image.load()
            self.width = self.image.size[0]
            self.height = self.image.size[1]
            self.luminance = self.getLuminanceFromRGB()
            

            '''Adding details back'''
            for x in range(0,self.width):
                for y in range(0,self.height):
                    print(str(self.luminance[x,y]))
                    self.luminance[x,y] = self.luminance[x,y]*Ldetail[x,y]
            '''Modifying the image luminance'''
            self.modifyLuminance(self.luminance)
            print("Image Transformed.")
            return self

                