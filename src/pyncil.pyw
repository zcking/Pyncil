#!/usr/bin/python3

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
import sys, os
import configparser
from multiprocessing import Process


class PyncilApp(QMainWindow):
    """Top-level Application for Pyncil IDE"""
    def __init__(self, parent=None):
        super(PyncilApp, self).__init__(parent)

        self.appTitle = 'Pyncil'
        self.currentFileName = 'Untitled'
        self.currentFilePath = os.getcwd()
        self.firstSave = True

        # Load the configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/settings.ini')

        # Set sizing
        self.resize(900, 700)

        # Create the widgets
        self.makeWidgets()

    def makeWidgets(self):
        """Create and setup the widgets"""
        # Main editor
        self.setupEditor()
        self.setCentralWidget(self.editor)

        # Status bar
        self.status_bar = self.statusBar()

        # Menus
        self.menu_bar = self.menuBar()
        self.setupFileMenu()
        self.setupEditMenu()
        self.setupToolsMenu()
        self.setupHelpMenu()

        # Connections
        self.makeConnections()

        # Initial UI Updates
        self.updateStatusBar()
        self.updateTitleBar()

    def setupEditor(self):
        self.font = QFont()
        try:
            self.font.setFamily(self.config['Editor']['Font'])
            self.font.setFixedPitch(self.config.getboolean('Editor', 'FixedPitch'))
            self.font.setPointSize(self.config.getint('Editor', 'FontSize'))
            self.font.setWordSpacing(self.config.getfloat('Editor', 'WordSpacing'))
        except Exception as e:
            self.font.setFamily('Courier')
            self.font.setFixedPitch(True)
            self.font.setPointSize(11)

        self.editor = QTextEdit()
        self.editor.setFont(self.font)

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
        self.menu_bar.addMenu(self.fileMenu)

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
        self.menu_bar.addMenu(self.editMenu)

    def setupToolsMenu(self):
        self.toolsMenu = QMenu('&Tools')
        self.toolsMenu.addAction('&Run (Python 3)', self.runWithPython3, 'Ctrl+B')
        self.toolsMenu.addAction('R&un (Python 2)', self.runWithPython2, 'Ctrl+Shift+B')
        self.toolsMenu.addAction('&Fix Indentation', self.tabify, 'Ctrl+Shift+T')
        self.menu_bar.addMenu(self.toolsMenu)

    def setupHelpMenu(self):
        self.helpMenu = QMenu('&Help')
        self.helpMenu.addAction('&About', self.about)
        self.helpMenu.addAction('&View Source', self.viewSource)
        self.menu_bar.addMenu(self.helpMenu)

    def makeConnections(self):
        # Status bar updates
        self.editor.cursorPositionChanged.connect(self.updateStatusBar)
        self.editor.textChanged.connect(self.updateStatusBar)

        # Title bar updates
        self.connect(self, SIGNAL('currentFileNameChanged'), self.updateTitleBar)

    def updateStatusBar(self):
        # Get current line no. and col.
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber()
        self.status_bar.showMessage('Ln {}, Col {}'.format(line, col))

    def updateTitleBar(self):
        self.setWindowTitle('{} - {} ({})'.format(
            self.appTitle, 
            self.currentFileName,
            self.currentFilePath
        ))

    def newFile(self):
        """Clears the text editor and sets the filename to 'Untitled'. 
        The first time the user tries to 'Save' the file, it will use the 
        'Save As' dialog."""
        self.editor.clear()
        self.currentFileName = 'Untitled'
        self.currentFilePath = os.getcwd()
        self.firstSave = True
        self.emit(SIGNAL('currentFileNameChanged'))
    
    def newWindow(self):
        os.startfile(__file__)

    def openFile(self, path=None):
        if not path:
            path = QFileDialog.getOpenFileName(self, 'Open File', 
                '', 'Python Files (*.py *.pyw)')
        
        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()

                try:
                    # Python 3
                    text = str(text, encoding='ascii')
                except TypeError:
                    # Python 2
                    text = str(text)

                self.editor.setPlainText(text)

            self.currentFilePath = path
            self.currentFileName = path.split('/')[-1]
            self.emit(SIGNAL('currentFileNameChanged'))

    def saveFile(self):
        if self.firstSave:
            self.currentFilePath = QFileDialog.getSaveFileName(self, 'Save File')
            self.currentFileName = self.currentFilePath.split('/')[-1]
            self.firstSave = False

        with open(self.currentFilePath, 'w') as f:
            f.write(self.editor.toPlainText())

        self.emit(SIGNAL('currentFileNameChanged'))

    def saveFileAs(self):
        self.currentFilePath = QFileDialog.getSaveFileName(self, 'Save As')
        self.currentFileName = self.currentFilePath.split('/')[-1]
        self.firstSave = False

        with open(self.currentFilePath, 'w') as f:
            f.write(self.editor.toPlainText())

        self.emit(SIGNAL('currentFileNameChanged'))

    def openPreferences(self):
        self.currentFilePath = os.path.join(os.getcwd(), 'config/settings.ini')
        self.currentFileName = 'settings.ini'
        self.firstSave = False

        with open(self.currentFilePath, 'r') as f:
            self.editor.clear()
            self.editor.setText(f.read())

        self.emit(SIGNAL('currentFileNameChanged'))

    def closeFile(self):
        self.currentFileName = 'Untitled'
        self.currentFilePath = os.getcwd()
        self.firstSave = True
        self.editor.clear()

        self.emit(SIGNAL('currentFileNameChanged'))

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editMenu.redo()

    def cut(self):
        self.editor.cut()

    def copy(self):
        self.editor.copy()

    def paste(self):
        self.editor.paste()

    def selectAll(self):
        self.editor.selectAll()

    def find(self):
        pass

    def replace(self):
        pass

    def runWithPython2(self):
        pass

        try:
            if self.currentFileName.endswith('.pyw'):
                python_path = self.config['Python']['Python2PathW']
            elif self.currentFileName.endswith('.py'):
                python_path = self.config['Python']['Python2Path']
            else:
                QMessageBox.warning(self, 
                    'The current file ({}) is not a Python program'.format(self.currentFileName
                ))
                return
            os.system(python_path + ' ' + self.currentFilePath)
        except Exception as e:
            error = QErrorMessage(self)
            error.show()
            error.showMessage('Could not run the current file with Python 2. '
                'Perhaps try checking your Python 2 path in the preferences.\n' + str(e))

    def runWithPython3(self):
        pass

        try:
            if self.currentFileName.endswith('.pyw'):
                python_path = self.config['Python']['Python3PathW']
            elif self.currentFileName.endswith('.py'):
                python_path = self.config['Python']['Python3Path']
            else:
                QMessageBox.warning(self, 
                    'The current file ({}) is not a Python program'.format(self.currentFileName
                ))
                return
            os.system(python_path + ' ' + self.currentFilePath)
        except Exception as e:
            error = QErrorMessage(self)
            error.show()
            error.showMessage('Could not run the current file with Python 3. '
                'Perhaps try checking your Python 3 path in the preferences.\n' + str(e))

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
    sys.exit(app.exec_())