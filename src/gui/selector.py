'''
Created on 31 Dec 2013

@author: green
'''

from PyQt4 import QtCore, QtGui
import operators
from trackingslider import TrackingSlider
import inspect
import sys

class AlgorithmSelector(QtGui.QDialog):
    """ The top level widget for the Interface Demonstrator application """
    def __init__(self):
        super(AlgorithmSelector, self).__init__()
        self.initUI()
        
    def  initUI(self):
        self.widgetList = []               # Widgets in the current control panel
        self.operatorList = []             # Available operator classes

        opSelect = QtGui.QComboBox(self)
        for name, obj in inspect.getmembers(operators):
            if inspect.isclass(obj):
                opSelect.addItem(obj().opName())
                self.operatorList.append(obj)
        
        # Initially expect to invoke the first operator in the operators
        # module (probably No Operation).
        self.theOperator = self.operatorList[0]()
        
        # Call my onNewOp method whenever the selected operator changes
        opSelect.currentIndexChanged.connect(self.onNewOp)
        
        # Build the left vertical box layout.
        # First, the operator selection combobox
        self.addWidget(opSelect)
        #self.vboxleft.addWidget(opSelect)
        # Then the control panel. bildWidget will return a single compound widget
        # containing all the controls the operator desires.
        controls = self.buildWidget(self.theOperator.getGuiComponents(), self)
        self.addWidget(controls)
        # Add a button to invoke the operator once all the controls are set
        goButton = QtGui.QPushButton("Try it", self)
        # When the button is clicked, call my onClicked method
        goButton.clicked.connect(self.onClicked)
        
        self.addWidget(goButton)
        #self.leftbox.setLayout(self.vboxleft)
        
        # Similarly for the right vertical box.
        # The text input and output widgets have to be class members
        # so we can read and update them later.
        self.userInput = QtGui.QLineEdit(self)
        self.outputDisplay = QtGui.QLabel(self)
        self.addWidget(self.userInput)
        self.addWidget(self.outputDisplay)
        #rightbox.setLayout(vboxright)    
        
        # Add the two vertical boxes hbox and adopt this as my layout
        #hbox.addWidget(self.leftbox)
        #hbox.addWidget(rightbox)
        #self.setLayout(hbox)
    
    def onClicked(self):
        """ Receives a signal whenever the user wants to invoke the operator
            The input text is passed to the operator's invoke function followed
            by the other parameters it needs. See also getArgsFromGui() """
        
        # use the current operator's invoke method. My getArgsFromGui method
        # returns a list of arguments; the * operator explodes a single list into
        # the required parameters. Display the result of such invokation.
        result = self.theOperator.invoke(self.userInput.text(),
                                         *self.getArgsFromGui())
        self.outputDisplay.setText(result)
    
    def onNewOp(self, i):
        
        win2 = AlgorithmSelector()
        win2.show()
        """ Receives a signal whenever the user wants to change the operator.
              The current list of widgets in the control panel is cleared, and
              a new one built. The old control panel widget is removed from the
              left QVBoxLayout and replaced with the new one. """
        print "new op: {}".format(i)
        self.widgetList = []
          
        # The old control panel is always item 1 (just below the operator combobox)
        oldItem = self.vboxleft.takeAt(1)
          
        # Update the current operator and build a new control panel
        # Insert the resulting widget into the QVBoxLayout to replace the one removed
        self.theOperator = self.operatorList[i]()
        controls = self.buildWidget(self.theOperator.getGuiComponents(), self.leftbox)    
        self.vboxleft.insertWidget(1, controls)
          
        # Boilerplate to dispose of the control panel widget safely.
        # If it's a widget, mark it for deletion at a convenient time.
        # If it's a layout, clear it.
        # (it should always be a widget, but you can't be too careful)
        oldWidget = oldItem.widget()
        if oldWidget is not None:
            oldWidget.deleteLater()
        else:
            self.clearLayout(oldItem.layout())
        
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


