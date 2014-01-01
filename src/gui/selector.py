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
        #self.initUI(operator)
        
    #def  initUI(self, operator):
        
        self.widgetList = []
        self.operatorList = []
        
        hbox = QtGui.QHBoxLayout()
    
        self.vboxleft = QtGui.QVBoxLayout()
        self.leftbox = QtGui.QWidget()
        self.vboxleft.setAlignment(QtCore.Qt.AlignTop)
        vboxright = QtGui.QVBoxLayout()
        rightbox = QtGui.QWidget()
        
        for name, obj in inspect.getmembers(operators):
            if inspect.isclass(obj):
                self.operatorList.append(obj)
        
        self.theOperator = self.operatorList[0]()
        self.onNewOp(operator)
        
        controls = self.buildWidget(self.theOperator.getGuiComponents(), self.leftbox)
        self.vboxleft.addWidget(controls)
        # Add a button to invoke the operator once all the controls are set
        
        #self.buttonBox = QtGui.QDialogButtonBox(self.leftbox)
        #self.buttonBox.setGeometry(QtCore.QRect(150, 250, 341, 32))
        #self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        #self.buttonBox.setObjectName("buttonBox")
        
        
        
        #self.goButton = QtGui.QPushButton("Try it", self)
        # When the button is clicked, call my onClicked method
        #self.connect(self.goButton, QtCore.SIGNAL("accepted()"), Dialog.accept, SLOT(GetDialogOutput())
        #self.connect(self.goButton, QtCore.SIGNAL("done ( int r )"), self.onClicked);
        #self.result = self.goButton.clicked.connect(self.onClicked)
        
        
        self.acceptButton = QtGui.QPushButton('Accept')
        self.cancelButton = QtGui.QPushButton('Cancel')
        
        self.vboxleft.addWidget(self.acceptButton)
        self.vboxleft.addWidget(self.cancelButton)
        
        self.acceptButton.connect(self.acceptButton, QtCore.SIGNAL("clicked()"), Dialog.accept)
        #self.result = self.acceptButton.connect(self.onClicked())
        self.cancelButton.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), Dialog.reject)
        
       #self.goButton.clicked.connect(self.accept)
        #self.goButton.clicked(self.getValues())
        #QObject.connect(self.goButton,SIGNAL("clicked()"),self.close())

        self.leftbox.setLayout(self.vboxleft)
        
        # Similarly for the right vertical box.
        # The text input and output widgets have to be class members
        # so we can read and update them later.
        #self.userInput = QtGui.QLineEdit(self)
        #self.outputDisplay = QtGui.QLabel(self)
        #vboxright.addWidget(self.userInput)
        #vboxright.addWidget(self.outputDisplay)
        rightbox.setLayout(vboxright)    
        
        # Add the two vertical boxes hbox and adopt this as my layout
        hbox.addWidget(self.leftbox)
        hbox.addWidget(rightbox)
        Dialog.setLayout(hbox)
        
        Dialog.setObjectName("Dialog")
        
    
    def onClicked(self):
        """ Receives a signal whenever the user wants to invoke the operator
            The input text is passed to the operator's invoke function followed
            by the other parameters it needs. See also() """
        
        # use the current operator's invoke method. My getArgsFromGui method
        # returns a list of arguments; the * operator explodes a single list into
        # the required parameters. Display the result of such invocation.
        self.result = self.theOperator.invoke(self.getArgsFromGui())
        #self.emit(QtCore.SIGNAL("resultSignal(PyQt_PyObject)"), self.result)

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
        layout = QtGui.QVBoxLayout()
        for widget in components:
            t = widget[0]
            if t == operators.Operator.Checkbox:
                cbw = QtGui.QCheckBox(widget[1], self)
            elif t == operators.Operator.Slider:
                cbw = TrackingSlider(widget[1], widget[2], widget[3])
            # Each control box widget created is appended to the layout and to the
            # list of widgets in the current layout, so an appropriate parameter set
            # can be formed later
            layout.addWidget(cbw)
            self.widgetList.append(cbw)
        newWidget.setLayout(layout)
        return newWidget
    
    def getArgsFromGui(self):
        # Read the values set on the control panel widgets to create an argument list """
        args = []
        for widget in self.widgetList:
            if isinstance(widget, QtGui.QCheckBox):
                args.append(widget.isChecked())
            elif isinstance(widget, TrackingSlider):
                args.append(widget.value())
        return args


