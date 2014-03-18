from PIL import Image
import os, os.path
import sys, string
import numpy as np
import hdr
import realisticImages

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
    
    def bilateralFilter(self, data, sigmaRange, sigmaSpatial):
        
        edge = data
        
        edgeMin = np.min(edge)
        edgeMax = np.max(edge)
        
        edgeDelta = edgeMax - edgeMin
    
        samplingRange = sigmaRange
        samplingSpatial = sigmaSpatial
        
        '''parameters'''
        derivedSigmaSpatial = sigmaSpatial/samplingSpatial
        derivedSigmaRange   = sigmaRange/samplingRange
        
        paddingXY = np.floor(2*derivedSigmaSpatial) + 1
        paddingZ = np.floor(2*derivedSigmaRange) + 1
        
        derivedSigmaSpatialFl = np.zeros(shape=(derivedSigmaSpatial))
        derivedSigmaRangeFl = np.zeros(shape=(derivedSigmaRange))        
        
        for i in range(0, len(derivedSigmaSpatial)):
            
            derivedSigmaSpatialFl[i] = np.floor(2*derivedSigmaSpatial[i])+1        
        
        for i in range(0, len(derivedSigmaRange)):
            
            derivedSigmaRangeFl[i] = np.floor(2*derivedSigmaRange[i]) + 1
        
        '''allocate 3D grid'''
        downsampledDepth  = np.floor(edgeDelta/samplingRange) + 1 + 2 * paddingZ
        downsampledWidth  = np.floor((self.width-1) / samplingSpatial ) + 1 + 2 * paddingXY
        downsampledHeight = np.floor((self.height-1)/ samplingSpatial ) + 1 + 2 * paddingXY
    
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
        for k in range(0, np.size(dz)):
            dataZ = data(k)
            ''' traverses the image column wise, same as di( k )'''
            #if ~isnan(dataZ):
            
            '''solve how to treat K!!!'''
            dik = di(k)
            djk = dj(k)
            dzk = dz(k)
        
                gridData( dik, djk, dzk ) = gridData( dik, djk, dzk ) + dataZ;
                gridWeights( dik, djk, dzk ) = gridWeights( dik, djk, dzk ) + 1;
                
        
        '''make gaussian kernel'''
        kernelWidth  = 2 * derivedSigmaSpatial + 1
        kernelHeight = kernelWidth
        kernelDepth  = 2 * derivedSigmaRange + 1
        
        halfKernelWidth  = np.floor(kernelWidth / 2 )
        halfKernelHeight = np.floor(kernelHeight / 2 )
        halfKernelDepth  = np.floor(kernelDepth / 2 )
        
        if (kernelWidth & 0x1):
            gridX=np.linspace(-halfkernelWidth, halfkernelWidth+1, kernelWidth+1)
        else:
            gridX=np.linspace(-halfkernelWidth, halfkernelWidth, kernelWidth+1)
        if (kernelHeight & 0x1):
            gridY=np.linspace(-halfkernelWidth, halfkernelHeighth+1, kernelHeight+1)
        else:
            gridY=np.linspace(-halfkernelWidth, halfkernelHeighth, kernelHeight+1)
        if (kernelDepth & 0x1):
            gridZ=np.linspace(-halfkernelDepth, halfkernelDepth+1, kernelDepth+1)
        else:
            gridZ=np.linspace(-halfkernelDepth, halfkernelDepth, kernelDepth+1)
         
        gridX, gridY, gridZ = np.meshgrid( gridX, gridY, gridZ)
        
        gridRSquared = np.zeros(shape = (kernelDepth + 1, kernelWidth+1, kernelHeight + 1))
        kernel = gridRSquared
        
        '''TO-DO:figure out indices'''
        for x in range(0, kernelHeight+1):
            for y in range(0, kernelWidth):
                for x in range(0, kernelDepth):
                    gridRSquared[z,x,y] = (np.power(gridX[z,x,y],2) + np.power(gridX[z,x,y],2))/(np.power(derivedSigmaSpatial,2))+(np.power(gridZ[z,x,y],2))/(np.power(derivedSigmaRange,2))
                    kernel[z,x,y] = np.exp(-0.5 * gridRSquared[z,x,y])
        
        '''convolve'''
        blurredGridData = self.convolve2d( gridData, kernel)
        blurredGridWeights = self.convolve2d( gridWeights, kernel)
        
        '''divide'''
        blurredGridWeights( blurredGridWeights == 0 ) = -2; # avoid divide by 0, won't read there anyway
        normalizedBlurredGrid = blurredGridData ./ blurredGridWeights
        normalizedBlurredGrid( blurredGridWeights < -1 ) = 0 #put 0s where it's undefined
        
        '''for debugging'''
        '''blurredGridWeights( blurredGridWeights < -1 ) = 0; % put zeros back'''
        
        '''upsample'''
        [ jj, ii ] = meshgrid( 0 : self.width - 1, 0 : self.height - 1 ); # meshgrid does x, then y, so output arguments need to be reversed
        '''no rounding'''
        di = ( ii / samplingSpatial ) + paddingXY + 1;
        dj = ( jj / samplingSpatial ) + paddingXY + 1;
        dz = ( edge - edgeMin ) / samplingRange + paddingZ + 1;
        
        '''interpn takes rows, then cols, etc
        i.e. size(v,1), then size(v,2), ...'''
        output = interpn( normalizedBlurredGrid, di, dj, dz );
                
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
        
        imgFil = self.bilateralFilter(tmp,rangeS,spatialS)

        '''Extracting Base and Detail Layers'''
        '''Removing 0'''
        for x in range(0,self.width):
            for y in range(0, self.height):
                Base[x,y]=np.power(2,imgFil[x,y])-1
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
            
            for z in range(0, col):
                for x in range(0,self.width):
                    for y in range(0,self.height):
                        lumChan[x,y]=lumChan[x,y]*Lbase[x,y,z]
            
            '''save img into a temporary location'''
            self.luminance = lumChan            
            tempFile = self.saveTemp()
            
            Lda = 0
            LdMax = 0
            CMax = 0            
            
            image = realisticImages.tumblinAndRushmeier(tempFile, Lda, LdMax,CMax, 1)
            imgOut = image.transform()

            '''Adding details back'''
            for x in range(0,self.width):
                for t in range(0,self.height):
                    imgOut[x,y] = imgOut[x,y]*Ldetail[x,y,z]
            '''Modifying the image luminance'''
            self.modifyLuminance(imgOut)
            return self

                