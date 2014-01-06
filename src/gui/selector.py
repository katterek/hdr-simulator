'''
Created on 31 Dec 2013

@author: green
'''

from PyQt4 import QtCore, QtGui
import operators
from trackingslider import TrackingSlider
import inspect
import sys

class AlgorithmSelector(object):
    """ The top level widget for the Interface Demonstrator application """
    def setupUI(self, Dialog, operator):
        
        Dialog.setObjectName("Dialog")
        self.widgetList = []
        self.operatorList = []
        
        hbox = QtGui.QHBoxLayout()
    
        self.vboxleft = QtGui.QVBoxLayout()
        self.leftbox = QtGui.QWidget()
        self.vboxleft.setAlignment(QtCore.Qt.AlignTop)
        self.vertbox = QtGui.QWidget()
        self.vboxvert = QtGui.QHBoxLayout()
        
        '''retrieving available operator'''
        for name, obj in inspect.getmembers(operators):
            if inspect.isclass(obj):
                self.operatorList.append(obj)
        
        self.theOperator = self.operatorList[0]()
        
        '''custom parameter box constructed depending on the index passed'''
        self.onNewOp(operator)
        
        '''buttons added and connected'''
        self.acceptButton = QtGui.QPushButton('Accept')
        self.cancelButton = QtGui.QPushButton('Cancel')
        
        self.vboxvert.addWidget(self.acceptButton)
        self.vboxvert.addWidget(self.cancelButton)
        
        self.acceptButton.connect(self.acceptButton, QtCore.SIGNAL("clicked()"), Dialog.accept)
        self.cancelButton.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), Dialog.reject)
        
        '''setting up layouts'''
        self.vertbox.setLayout(self.vboxvert) 
        self.vboxleft.addWidget(self.vertbox)
        self.leftbox.setLayout(self.vboxleft)   
        
        hbox.addWidget(self.leftbox)
        Dialog.setLayout(hbox)
        
        
    def getParameters(self):
        """ Receives a signal whenever the user wants to invoke the operator
            The input text is passed to the operator's invoke function followed
            by the other parameters it needs. See also() """
        
        self.result = self.theOperator.invoke(self.getArgsFromGui())

        return self.result
    
    def onNewOp(self, i):
        
        """ Receives a signal whenever the user wants to change the operator.
              The current list of widgets in the control panel is cleared, and
              a new one built. The old control panel widget is removed from the
              left QVBoxLayout and replaced with the new one. """
        self.widgetList = []
  
        self.theOperator = self.operatorList[i]()
        controls = self.buildWidget(self.theOperator.getGuiComponents(), self.leftbox)    
        self.vboxleft.insertWidget(1, controls)
        
    def buildWidget(self, components, parent=None):
        """ Given a list of components, build a control panel widget with the
        given parent. Control panel items are documented in the operators module.
        Currently implemented control panel componets are;
        Checkbox
        Slider
        """
        newWidget = QtGui.QWidget(parent)
        layout = QtGui.QGridLayout()
        i=0
        j=0
        for widget in components:
            t = widget[0]
            if t == operators.Operator.Checkbox:
                cbw = QtGui.QCheckBox(widget[1])
            elif t == operators.Operator.Slider:
                cbw = TrackingSlider(widget[1], widget[2], widget[3])
            ''' Each control box widget created is appended to the layout and to the
            list of widgets in the current layout, so an appropriate parameter set
             can be formed later'''
            layout.addWidget(cbw, j, i)
            self.widgetList.append(cbw)
            if (i==4):
                i = 0
                j = j + 1
            else:
                i = i + 1
        newWidget.setLayout(layout)
        return newWidget
    
    def getArgsFromGui(self):
        ''' Read the values set on the control panel widgets to create an argument list '''
        args = []
        for widget in self.widgetList:
            if isinstance(widget, QtGui.QCheckBox):
                args.append(widget.isChecked())
            elif isinstance(widget, TrackingSlider):
                args.append(widget.value())
        return args


