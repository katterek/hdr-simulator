'''
Created on 31 Dec 2013

@author: green
'''
from PyQt4 import QtGui, QtCore

class TrackingSlider(QtGui.QWidget):
    def __init__(self, label, minimum, maximum, parent=None):
        super(TrackingSlider, self).__init__()
        
        self.theLabel = QtGui.QLabel(label, parent)
        self.theLCDNumber = QtGui.QLCDNumber(parent)
        self.theLCDNumber.setFixedHeight(18)
        self.theLCDNumber.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.theLCDNumber.display(minimum)
        self.theSlider = QtGui.QSlider(QtCore.Qt.Horizontal, parent)
        self.theSlider.setRange(minimum, maximum)
        
        annotationLayout = QtGui.QHBoxLayout()
        annotation = QtGui.QWidget(parent)
        annotationLayout.addWidget(self.theLabel)
        annotationLayout.addWidget(self.theLCDNumber)
        annotation.setLayout(annotationLayout)
        
        self.theLayout = QtGui.QVBoxLayout()
        self.theLayout.setSpacing(1)
        self.theLayout.addWidget(annotation)
        self.theLayout.addWidget(self.theSlider)
        self.setLayout(self.theLayout)
        
        self.theSlider.valueChanged.connect(self.theLCDNumber.display)
    def value(self):
        return self.theLCDNumber.value()