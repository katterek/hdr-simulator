import gui
from PyQt4 import QtGui
import sys

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    imageViewer = gui.ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())