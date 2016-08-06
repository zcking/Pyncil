#!/usr/bin/python3

"""
File: pyncil.pyw
Author: Zachary King
Copyright (2016)

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
import webbrowser

from ext import *
from ext import highlighter


class Container(QWidget):
    def __init__(self, parent=None):
        super(Container, self).__init__(parent)

        self.container = QHBoxLayout()


class PyncilApp(QMainWindow):
    """Top-level Application for Pyncil IDE"""
    def __init__(self, parent=None):
        super(PyncilApp, self).__init__(parent)

        self.appTitle = 'Pyncil'
        self.currentFileName = 'Untitled'
        self.currentFilePath = os.getcwd()
        self.firstSave = True
        self.findDlg = None

        # Load the configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/settings.ini')

        self.lineNumbersOn = self.config.getboolean('Editor', 'ShowLineNumbers')

        # Set sizing
        self.resize(900, 700)

        # Create the widgets
        self.makeWidgets()

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.editor, self.editor.viewport()):
            self.numberBar.update()
            return False
        return QFrame.eventFilter(object, event)

    def makeWidgets(self):
        """Create and setup the widgets"""
        self.container = Container()

        self.numberBar = numberbar.NumberBar()

        if self.lineNumbersOn:
            self.container.container.addWidget(self.numberBar)

        # Main editor
        self.setupEditor()
        
        self.container.setLayout(self.container.container)
        
        self.numberBar.setTextEdit(self.editor)
        self.setCentralWidget(self.container)

        self.editor.installEventFilter(self)
        self.editor.viewport().installEventFilter(self)

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
        self.editor = QTextEdit()
        self.container.container.addWidget(self.editor)
        self.setEditorStyle()

    def setEditorStyle(self):
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
            self.font.setWordSpacing(1.0)

        # Critical - if you are extending this editor with your own highlighter, 
        # this is the line that should be changed
        try:
            self.highlighter = eval(
                'highlighter.' + self.config['Extensions']['Highlighter'] + '(self.editor.document())')
            self.editor.setPalette(self.highlighter.getPalette())
        except Exception as e:
            self.makeErrorPopup(msg='Unable to load the Highlighter speficied in Extensions -> Highlighter')
            print(e)
            self.highlighter = None

        self.editor.setTabStopWidth(40)
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
        self.editMenu.addAction('&Find / Replace', find.Find(self).show, 'Ctrl+F')
        self.menu_bar.addMenu(self.editMenu)

    def setupToolsMenu(self):
        self.toolsMenu = QMenu('&Tools')
        self.toolsMenu.addAction('&Run (Python 3)', self.runWithPython3, 'Ctrl+B')
        self.toolsMenu.addAction('R&un (Python 2)', self.runWithPython2, 'Ctrl+Shift+B')
        self.toolsMenu.addAction('&Fix Indentation', self.tabify, 'Ctrl+Shift+T')
        self.menu_bar.addMenu(self.toolsMenu)

    def setupHelpMenu(self):
        self.helpMenu = QMenu('&Help')
        self.helpMenu.addAction('&Help', self.help)
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
        os.startfile(__file__) # Temporary solution?

    def openFile(self, path=None):
        if not path:
            path = QFileDialog.getOpenFileName(self, 'Open File', 
                '', 'Python Files (*.py *.pyw)')
        
        if path:
            self.firstSave = False
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
        # Create the Preferences dialog
        dlg = preferences.PreferencesDlg(self)
        dlg.show()
        return
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

    def runWithPython2(self):
        try:
            python_path = self.config['Python']['Python2Path'] + 'python'
            isGUI = self.currentFileName.endswith('.pyw')

            if isGUI:
                python_path += 'w'
            
            if self.currentFileName.endswith('.py') or isGUI:
                os.system(python_path + ' -i ' + self.currentFilePath)
            else:
                self.makeErrorPopup(msg='The current file ({}) is not a Python file'.format(self.currentFileName))
        except Exception as e:
            self.makeErrorPopup(msg='Could not run the current file with Python 2. '
                'Perhaps try checking your Python 2 path in the preferences.\n' + str(e))

    def runWithPython3(self):
        try:
            python_path = self.config['Python']['Python3Path'] + 'python'
            isGUI = self.currentFileName.endswith('.pyw')

            if isGUI:
                python_path += 'w'
            
            if self.currentFileName.endswith('.py') or isGUI:
                os.system(python_path + ' -i ' + self.currentFilePath)
            else:
                self.makeErrorPopup(msg='The current file ({}) is not a Python file'.format(self.currentFileName))
        except Exception as e:
            self.makeErrorPopup(msg='Could not run the current file with Python 3. '
                'Perhaps try checking your Python 3 path in the preferences.\n' + str(e))

    def tabify(self):
        try:
            text = self.editor.toPlainText()
            if self.config.getboolean('Editor', 'UseSpaces'):
                text = text.replace('\t', ' ' * self.config.getint('Editor', 'SpacesPerTab'))
            else:
                text = text.replace(' ' * self.config.getint('Editor', 'SpacesPerTab'), '\t')
            self.editor.clear()
            self.editor.setText(text)
        except Exception as e:
            self.makeErrorPopup(msg='Unable to fix indentation')
            print(e)

    def about(self):
        webbrowser.open('https://github.com/zach-king/Pyncil/blob/master/README.md')

    def help(self):
        webbrowser.open('https://github.com/zach-king/Pyncil/blob/master/HELP.md')

    def viewSource(self):
        webbrowser.open('https://www.github.com/zach-king/Pyncil.git')

    def makeErrorPopup(self, title='Oops', msg='Something went wrong...'):
        popup = QErrorMessage(self)
        popup.setWindowTitle(title)
        popup.showMessage(msg)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyncilApp()
    window.show()
    sys.exit(app.exec_())