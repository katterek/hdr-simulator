'''
Created on 31 Dec 2013

@author: green
'''


__author__ = 'Nick Bailey <nick@n-ism.org>'
__version__ = 1.0

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

class ToneRepOperator(Operator):
    """ Provides control over Tone Reproduction parameters """

    def opName(self):
        return 'Tone Reproduction'
    def getGuiComponents(self):
        return [ [Operator.Slider, 'Key:', 1, 11],[Operator.Slider, 'Gamma:', 0.0, 2.0],
                [Operator.Slider, 'Phi:', 1, 16],[Operator.Slider, 'Threshold:', 0.01, 1.00], 
                [Operator.Slider, 'Range S:', 1, 10],[Operator.Checkbox, 'Use Default Values']]
        
    
    def invoke(self, val):
        key=val[0]
        gamma=val[1] 
        phi=val[2]
        threshold=val[3]
        srange=val[4]
        default = val[5]
        return key, gamma, phi, threshold, srange, default


class Shape(Operator):
    """ Draw a triangle or square of a given dimension using # signs
    Ignores the input value """
    
    def opName(self):
        return 'Pretty Shape'
    
    def getGuiComponents(self):
        return [[Operator.Slider, 'Size:', 1, 6] ]
             
    def invoke(self, values):
        val1 = values[0]
        val2 = values[1]
        return val1, val2


class Truncate(Operator):
    """ Miss out some characters from the beginning or end of the input """
    
    def opName(self):
        return 'Truncate'
    def getGuiComponents(self):
        return [ [Operator.Checkbox, 'Delete from end'],
             [Operator.Slider, 'Characters to omit:', 1, 10] ]
        
    def invoke(self,values):
        val1 = values[0]
        val2 = values[1]
        return val1, val2