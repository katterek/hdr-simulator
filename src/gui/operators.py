'''
Created on 31 Dec 2013

@author: green
'''

class Operator:
    """ The base class of all operators.
        This class performs no operation, and returns the string 'Unimplemented'
        
        Derived classes should override all methods of this class.
    """    
        
    # Enumeration of all of the expected gui components
    Checkbox, Slider = range(2)
    def opName(self):
        """ Return a short, human-readable description """
        return 'No operation'
  
    def getGuiComponents(self):
        """ Return a list of gui components needed to gather input parameters """
        return []
    
    def invoke(self, *_):
        # Perform the appropriate operation using the given parameters """#
        return 'Unimplemented'

class PhotoTMOOperator(Operator):
    """ Provides control over Phtographic Tone Reproduction parameters """

    def opName(self):
        return 'Photographic Tone Reproduction'
    def getGuiComponents(self):
        return [ [Operator.Slider, 'Key:', 1, 11],
                [Operator.Slider, 'Phi:', 1, 16],[Operator.Slider, 'Threshold:', 0.01, 0.5], 
                [Operator.Slider, 'Range S:', 1, 10],[Operator.Checkbox, 'Use Default Values']]
        
    
    def invoke(self, val):
        key=val[0] 
        phi=val[1]
        threshold=val[2]
        srange=val[3]
        default = val[4]
        return key, phi, threshold, srange, default
    
class gradientDomainCompression(Operator):
    """ Provides control over Gradient Domain Compression parameters """

    def opName(self):
        return 'Gradient Domain Compression'
    def getGuiComponents(self):
        return [ [Operator.Slider, 'fBeta:', 1, 11],[Operator.Checkbox, 'Use Default Values']]
        
    
    def invoke(self, val):
        fBeta=val[0]
        default = val[1]
        return fBeta, default

class TumblinAndRushmeier(Operator):
    """ Provides control over Realistic Images Tone Reproduction parameters """

    def opName(self):
        return 'Realistic Images Tone Reproduction'
    def getGuiComponents(self):
        return [[Operator.Slider, 'Lda:', 10, 30],[Operator.Slider, 'LdMax:', 30, 100],
                [Operator.Slider, 'CMax:', 30, 100], 
                [Operator.Checkbox, 'Use Default Values']]
        
    
    def invoke(self, val):
        Lda=val[0]
        LdMax=val[1]
        CMax=val[2]
        default = val[3]
        return Lda, LdMax, CMax, default