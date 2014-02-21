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
    
    def bilateralFilter(self, data, edge, edgeMin, edgeMax,sigmaSpatial, sigmaRange,samplingSpatial, samplingRange):
        
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

% parameters
derivedSigmaSpatial = sigmaSpatial / samplingSpatial;
derivedSigmaRange = sigmaRange / samplingRange;

paddingXY = floor( 2 * derivedSigmaSpatial ) + 1;
paddingZ = floor( 2 * derivedSigmaRange ) + 1;

% allocate 3D grid
downsampledWidth = floor( ( inputWidth - 1 ) / samplingSpatial ) + 1 + 2 * paddingXY;
downsampledHeight = floor( ( inputHeight - 1 ) / samplingSpatial ) + 1 + 2 * paddingXY;
downsampledDepth = floor( edgeDelta / samplingRange ) + 1 + 2 * paddingZ;

gridData = zeros( downsampledHeight, downsampledWidth, downsampledDepth );
gridWeights = zeros( downsampledHeight, downsampledWidth, downsampledDepth );

% compute downsampled indices
[ jj, ii ] = meshgrid( 0 : inputWidth - 1, 0 : inputHeight - 1 );

% ii =
% 0 0 0 0 0
% 1 1 1 1 1
% 2 2 2 2 2

% jj =
% 0 1 2 3 4
% 0 1 2 3 4
% 0 1 2 3 4

% so when iterating over ii( k ), jj( k )
% get: ( 0, 0 ), ( 1, 0 ), ( 2, 0 ), ... (down columns first)

di = round( ii / samplingSpatial ) + paddingXY + 1;
dj = round( jj / samplingSpatial ) + paddingXY + 1;
dz = round( ( edge - edgeMin ) / samplingRange ) + paddingZ + 1;

% perform scatter (there's probably a faster way than this)
% normally would do downsampledWeights( di, dj, dk ) = 1, but we have to
% perform a summation to do box downsampling
for k = 1 : numel( dz ),
       
    dataZ = data( k ); % traverses the image column wise, same as di( k )
    if ~isnan( dataZ  ),
        
        dik = di( k );
        djk = dj( k );
        dzk = dz( k );

        gridData( dik, djk, dzk ) = gridData( dik, djk, dzk ) + dataZ;
        gridWeights( dik, djk, dzk ) = gridWeights( dik, djk, dzk ) + 1;
        
    end
end

% make gaussian kernel
kernelWidth = 2 * derivedSigmaSpatial + 1;
kernelHeight = kernelWidth;
kernelDepth = 2 * derivedSigmaRange + 1;

halfKernelWidth = floor( kernelWidth / 2 );
halfKernelHeight = floor( kernelHeight / 2 );
halfKernelDepth = floor( kernelDepth / 2 );

[gridX, gridY, gridZ] = meshgrid( 0 : kernelWidth - 1, 0 : kernelHeight - 1, 0 : kernelDepth - 1 );
gridX = gridX - halfKernelWidth;
gridY = gridY - halfKernelHeight;
gridZ = gridZ - halfKernelDepth;
gridRSquared = ( gridX .* gridX + gridY .* gridY ) / ( derivedSigmaSpatial * derivedSigmaSpatial ) + ( gridZ .* gridZ ) / ( derivedSigmaRange * derivedSigmaRange );
kernel = exp( -0.5 * gridRSquared );

% convolve
blurredGridData = convn( gridData, kernel, 'same' );
blurredGridWeights = convn( gridWeights, kernel, 'same' );

% divide
blurredGridWeights( blurredGridWeights == 0 ) = -2; % avoid divide by 0, won't read there anyway
normalizedBlurredGrid = blurredGridData ./ blurredGridWeights;
normalizedBlurredGrid( blurredGridWeights < -1 ) = 0; % put 0s where it's undefined

% for debugging
% blurredGridWeights( blurredGridWeights < -1 ) = 0; % put zeros back

% upsample
[ jj, ii ] = meshgrid( 0 : inputWidth - 1, 0 : inputHeight - 1 ); % meshgrid does x, then y, so output arguments need to be reversed
% no rounding
di = ( ii / samplingSpatial ) + paddingXY + 1;
dj = ( jj / samplingSpatial ) + paddingXY + 1;
dz = ( edge - edgeMin ) / samplingRange + paddingZ + 1;

% interpn takes rows, then cols, etc
% i.e. size(v,1), then size(v,2), ...
output = interpn( normalizedBlurredGrid, di, dj, dz );
        
        return output
    
    def BilateralSeparation(self,img, simga_s, simga_r):
        %default parameters
        if(~exist('sigma_s')|~exist('sigma_r'))
            sigma_r=4
            sigma_s=0.5

        '''Base Layer'''
        tmp=np.log2(img+1)

        try
            imgFil = bilateralFilter(tmp,[],min(min(tmp)),max(max(tmp)),sigma_s,sigma_r)
        catch exception
            imgFil = bilateralFilter(tmp)

        Base=2.^(imgFil)-1

        '''Removing 0'''
        Base(find(Base<0))=0

        '''Detail Layer'''
        Detail=RemoveSpecials(img./Base);
        
        return Base, Detail

    
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

            image = realisticImages.tumblinAndRushmeier(self.imagePath, Lda, LdMax,CMax, default)
            hdrImage = image.transform()
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
                