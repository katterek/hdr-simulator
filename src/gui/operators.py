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
        return [ [Operator.Checkbox, 'Repeat'], [Operator.Slider, 'Key:', 0, 1],
             [Operator.Slider, 'White:', 1, 6],[Operator.Slider, 'Gamma:', 1, 6],
             [Operator.Slider, 'Phi:', 1, 6],[Operator.Slider, 'Threshold:', 1, 6],
             [Operator.Slider, 'Num:', 1, 6],[Operator.Slider, 'Low:', 1, 6],
             [Operator.Slider, 'High:', 1, 6],[Operator.Slider, 'Range S:', 1, 10]]
        
    
    def invoke(self, val, rep):
        print rep
        result = val
        if rep:
            result += ", " + result
        return result


class Shape(Operator):
    """ Draw a triangle or square of a given dimension using # signs
    Ignores the input value """
    
    def opName(self):
        return 'Pretty Shape'
    
    def getGuiComponents(self):
        return [ [Operator.Checkbox, 'Make Square'],
             [Operator.Slider, 'Size:', 1, 6] ]
             
    def invoke(self, val, isSquare, size):
        result = ''
        size = int(size)
        for i in range(size):
            if isSquare:
                result += size*'#'
            else:
                result += (i+1)*'#'
                result += '<br/>'
        return result


class Truncate(Operator):
    """ Miss out some characters from the beginning or end of the input """
    
    def opName(self):
        return 'Truncate'
    def getGuiComponents(self):
        return [ [Operator.Checkbox, 'Delete from end'],
             [Operator.Slider, 'Characters to omit:', 1, 10] ]
        
    def invoke(self, val, fromEnd, numChar):
        numChar = int(numChar)
        if fromEnd:
            return val[:-numChar]
        else:
            return val[numChar:]