from PyQt4 import QtGui, QtCore, Qt
import operators
import trackingslider
import sys
import selector
import hdr
import realisticImages
import reinhardPhotoTMO
import inspect
#import FastBilateralFilering #@UnresolvedImport
import gradientDomainCompression #@UnresolvedImport

class ImageViewer(QtGui.QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()
        self.widgetList = []               # Widgets in the current control panel
        self.operatorList = []             # Available operator classes

        '''toolbar'''
        self.toolbar = self.addToolBar('Algorithms')

        '''algorithm selection in the toolbar'''       
        
        opSelect = QtGui.QComboBox(self)
        for name, obj in inspect.getmembers(operators):
            if inspect.isclass(obj):
                opSelect.addItem(obj().opName())
                self.operatorList.append(obj)

        self.theOperator = self.operatorList[0]()
        opSelect.currentIndexChanged.connect(self.selectRender)

        self.toolbar.addWidget(opSelect)
        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Toolbar')    
        self.show()

        '''display window'''        
        self.printer = QtGui.QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("HDR Compare")
        self.resize(500, 400)       

    def open(self):
        '''open file'''
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
        if fileName:
            image = QtGui.QImage(fileName)
            if image.isNull():
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            self.imagePath = str(fileName)
            print "HDR object created"

    def save(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save File",QtCore.QDir.currentPath())
        hdr.HDR(str(self.tempFile)).saveImage(str(fileName))
        ##TO-DO:display window "FILE SAVED"

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QtGui.QMessageBox.about(self, "About HDR Simulator")
        
    def loadParameters(self,i,result):
        if(i==1):
            key=result[0]
            phi=result[1]
            threshold=result[2]
            srange=result[3]
            default=result[4]
            print("Key: "+ str(key) + ", Threshold:" + str(threshold) + " .Phi: " + str(phi) + ", SRange" + str(srange))
            image = reinhardPhotoTMO.reinhard(self.imagePath, key, threshold, phi, srange, default)
            hdrImage = image.transform()
        elif(i==0):
            fBeta=result[0]
            default=result[1]
            image = gradientDomainCompression.fattal(self.imagePath, fBeta, default)
            hdrImage = image.transform()
            
        elif(i==2):
            Lda=result[0]
            Lwa = result
            LdMax=result[1]
            CMax=result[2]
            default=result[3]
            image = realisticImages.tumblinAndRushmeier(self.imagePath, Lda, LdMax,CMax, default)
            hdrImage = image.transform()
            
        else:
            image=result
        
        '''display updated hdrImage'''
        self.tempFile = QtCore.QString(hdrImage.saveTemp())
        if self.tempFile:
            image = QtGui.QImage(self.tempFile)
            if image.isNull():
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % self.tempFile)
                return

            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

    def selectRender(self,i):
        
        Dialog = QtGui.QDialog()
        ui = selector.AlgorithmSelector()
        ui.setupUI(Dialog, i)
        Dialog.show()
                    
        if Dialog.exec_():
            result = ui.getParameters()
        self.loadParameters(i,result)
        
    def createActions(self):
        self.openAct = QtGui.QAction("&Open", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.saveAct = QtGui.QAction("&Save As", self, shortcut="Ctrl+S",
                triggered=self.save)

        self.printAct = QtGui.QAction("&Print", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.selectRenderAct = QtGui.QAction("Select Rendering Algorithm", self,
                triggered=self.selectRender)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())