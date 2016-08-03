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

        # Status bar
        self.statusBar = QStatusBar()

        # Menus
        self.menuBar = QMenuBar(self)
        self.setupFileMenu()
        self.setupEditMenu()
        self.setupToolsMenu()
        self.setupHelpMenu()
    
        self.menuBar.show()

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.editor)
        self.main_layout.addWidget(self.statusBar)
        self.setLayout(self.main_layout)

        # Connections
        self.editor.cursorPositionChanged.connect(self.updateStatusBar)
        self.editor.textChanged.connect(self.updateStatusBar)

        # Initial UI Updates
        self.updateStatusBar()

    def setupFileMenu(self):
        self.fileMenu = QMenu('&File')
        self.fileMenu.addAction('&New File', self.newFile, 'Ctrl+N')
        self.fileMenu.addAction('&New Window', self.newWindow, 'Ctrl+Shift+N')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('&Open File', self.openFile, 'Ctrl+O')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('&Save', self.saveFile, 'Ctrl+S')
        self.fileMenu.addAction('Save &As', self.saveFileAs, 'Ctrl+Shift+S')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('&Preferences', self.openPreferences)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('&Close File', self.closeFile, 'Ctrl+W')
        self.fileMenu.addAction('Close &Window', qApp.quit, 'Ctrl+Q')
        self.menuBar.addMenu(self.fileMenu)

    def setupEditMenu(self):
        self.editMenu = QMenu('&Edit')
        self.editMenu.addAction('&Undo', self.undo, 'Ctrl+Z')
        self.editMenu.addAction('&Redo', self.redo, 'Ctrl+Y')
        self.editMenu.addSeparator()
        self.editMenu.addAction('&Cut', self.cut, 'Ctrl+X')
        self.editMenu.addAction('C&opy', self.copy, 'Ctrl+C')
        self.editMenu.addAction('&Paste', self.paste, 'Ctrl+V')
        self.editMenu.addAction('&Select All', self.selectAll, 'Ctrl+A')
        self.editMenu.addSeparator()
        self.editMenu.addAction('&Find', self.find, 'Ctrl+F')
        self.editMenu.addAction('&Replace', self.replace, 'Ctrl+H')
        self.menuBar.addMenu(self.editMenu)

    def setupToolsMenu(self):
        self.toolsMenu = QMenu('&Tools')
        self.toolsMenu.addAction('&Run Python', self.run, 'Ctrl+B')
        self.toolsMenu.addAction('&Fix Indentation', self.tabify, 'Ctrl+Shift+T')
        self.menuBar.addMenu(self.toolsMenu)

    def setupHelpMenu(self):
        self.helpMenu = QMenu('&Help')
        self.helpMenu.addAction('&About', self.about)
        self.helpMenu.addAction('&View Source', self.viewSource)
        self.menuBar.addMenu(self.helpMenu)

    def updateStatusBar(self):
        # Get current line no. and col.
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        self.statusBar.showMessage('Ln {}, Col {}'.format(line, col))

    def newFile(self):
        pass
    
    def newWindow(self):
        pass

    def openFile(self):
        pass

    def saveFile(self):
        pass

    def saveFileAs(self):
        pass

    def openPreferences(self):
        pass

    def closeFile(self):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def cut(self):
        pass

    def copy(self):
        pass

    def paste(self):
        pass

    def selectAll(self):
        pass

    def find(self):
        pass

    def replace(self):
        pass

    def run(self):
        pass

    def tabify(self):
        pass

    def about(self):
        pass

    def viewSource(self):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyncilApp()
    window.show()
    app.exec_()