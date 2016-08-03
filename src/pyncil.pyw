"""
File: pyncil.pyw
Author: Zachary King

Description:
'Pyncil' is an open-sourcce, Python text editor. It is written 
Python 3 and uses Qt as the GUI framework, and is thus 
cross-platform. Pyncil is intended to be used specifically 
for writing Python.
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import configparser


class PyncilApp(QDialog):
    """Top-level Application for Pyncil IDE"""
    def __init__(self, parent=None):
        super(PyncilApp, self).__init__(parent)

        self.appTitle = 'Pyncil'
        self.currentFileName = ''

        # Minimum dimensions
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Create the widgets
        self.makeWidgets()

        if self.currentFileName != '':
            self.setWindowTitle('{0} - {1}'.format(self.appTitle, self.currentFileName))
        else:
            self.setWindowTitle(self.appTitle)

    def makeWidgets(self):
        """Create and setup the widgets"""
        # Main editor
        self.editor = QTextEdit()

        # Menus
        self.menuBar = QMenuBar(self)
        self.fileMenu = QMenu('&File')
        self.editMenu = QMenu('&Edit')
        self.toolsMenu = QMenu('&Tools')
        self.helpMenu = QMenu('&Help')
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.editMenu)
        self.menuBar.addMenu(self.toolsMenu)
        self.menuBar.addMenu(self.helpMenu)
        self.menuBar.show()

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.editor)
        self.setLayout(self.main_layout)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyncilApp()
    window.show()
    app.exec_()