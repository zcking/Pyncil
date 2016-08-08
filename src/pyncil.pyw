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
import tempfile

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
        self.madeChanges = False

        # Load the configuration
        self.loadConfig()

        self.lineNumbersOn = self.settings.getboolean('Editor', 'ShowLineNumbers')

        # Set sizing
        self.resize(900, 700)

        # Create the widgets
        self.makeWidgets()

        # App Icon
        self.setWindowIcon(QIcon('logo.png'))

    def loadConfig(self):
        self.settings = configparser.ConfigParser()
        self.settings.read('config/settings.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.settings['Editor']['theme'])

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary signals.
        if object in (self.editor, self.editor.viewport()):
            # For the indentation
            if event.type() == QEvent.KeyPress:
                key = (QKeyEvent)(event).key()
                if key == Qt.Key_Tab:
                    self.indent()
                    return True
                elif self.settings.getboolean('Editor', 'smartindent'): # Smart indent
                    if key == Qt.Key_Return or key == Qt.Key_Enter: 
                        self.enter()
                        return True
                    elif key == Qt.Key_Backspace:
                        self.backspace()
                        # return True # uncomment this line after implementing self.backspace() (smart backspace)

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
        self.madeChanges = False # UI Updates tend to trigger the textChanged signal. This counters that affect

    def setupEditor(self):
        self.editor = QTextEdit()
        self.container.container.addWidget(self.editor)
        self.setEditorStyle()

    def setEditorStyle(self):
        self.font = QFont()
        self.loadConfig()

        self.font.setFamily(self.settings.get('Editor', 'Font', fallback='Courier'))
        self.font.setFixedPitch(self.settings.getboolean('Editor', 'FixedPitch', fallback=True))
        self.font.setPointSize(self.settings.getint('Editor', 'FontSize', fallback=11))
        self.font.setWordSpacing(self.settings.getfloat('Editor', 'WordSpacing', fallback=1.0))

        # try:
        self.highlighter = eval(
            'highlighter.' + self.settings['Extensions']['Highlighter'] + '(self.editor.document())')
        self.editor.setPalette(self.highlighter.getPalette())
        # except Exception as e:
        #     self.makeErrorPopup(msg='Unable to load the Highlighter speficied in Extensions -> Highlighter')
        #     print(e)
        #     self.highlighter = highlighter.PythonHighlighter(self.editor.document())

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
        self.fileMenu.addAction('Close &Window', self.quit, 'Ctrl+Q')
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
        self.editMenu.addSeparator()
        self.editMenu.addAction('&Indent Line/Block', self.indent, 'Tab')
        self.editMenu.addAction('&Dedent Line/Block', self.dedent, 'Shift+Tab')
        self.editMenu.addSeparator()
        self.editMenu.addAction('Toggle Co&mment', self.comment, 'Ctrl+/')
        self.menu_bar.addMenu(self.editMenu)

    def setupToolsMenu(self):
        self.toolsMenu = QMenu('&Tools')
        self.toolsMenu.addAction('&Run (Python 3)', self.runWithPython3, 'Ctrl+B')
        self.toolsMenu.addAction('R&un (Python 2)', self.runWithPython2, 'Ctrl+Shift+B')
        self.toolsMenu.addAction('&Unify Indentation', self.tabify, 'Ctrl+Shift+T')
        self.menu_bar.addMenu(self.toolsMenu)

    def setupHelpMenu(self):
        self.helpMenu = QMenu('&Help')
        self.helpMenu.addAction('&Help', self.help)
        self.helpMenu.addAction('&About', self.about)
        self.helpMenu.addAction('&View Source', self.viewSource)
        self.menu_bar.addMenu(self.helpMenu)

    def makeChanges(self):
        self.madeChanges = True

    def makeConnections(self):
        # Status bar updates
        self.editor.cursorPositionChanged.connect(self.updateStatusBar)
        self.editor.textChanged.connect(self.updateStatusBar)
        self.editor.textChanged.connect(self.makeChanges)

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

    def updateUi(self):
        # Reload the config
        self.loadConfig()

        # Update status bar and title bar
        self.updateStatusBar()
        self.updateTitleBar()
        
        if self.settings.getboolean('Editor', 'ShowLineNumbers', fallback=False):
            self.numberBar.show()
        else:
            self.numberBar.hide()

        # Update text editor style
        self.setEditorStyle()
        self.editor.update()
        self.update()

    def newFile(self):
        """Clears the text editor and sets the filename to 'Untitled'. 
        The first time the user tries to 'Save' the file, it will use the 
        'Save As' dialog."""
        # Ask if want to save first, if changes have been made
        if self.madeChanges:
            reply = QMessageBox.question(self, "Save First?", 
            'You have unsaved changes. Would you like to save them before closing this file?',
                QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                if self.firstSave:
                    self.saveFileAs()
                else:
                    self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

        self.editor.clear()
        self.currentFileName = 'Untitled'
        self.currentFilePath = os.getcwd()
        self.firstSave = True
        self.emit(SIGNAL('currentFileNameChanged'))
    
    def newWindow(self):
        os.startfile(__file__) # Temporary solution?

    def openFile(self, path=None):
        # Ask if want to save first, if changes have been made
        if self.madeChanges:
            reply = QMessageBox.question(self, "Save First?", 
            'You have unsaved changes. Would you like to save them before closing this file?',
                QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                if self.firstSave:
                    self.saveFileAs()
                else:
                    self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

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
            fpath = QFileDialog.getSaveFileName(self, 'Save File')
            if fpath == '':
                return False
            
            self.currentFilePath = fpath
            self.currentFileName = self.currentFilePath.split('/')[-1]
            self.firstSave = False

        with open(self.currentFilePath, 'w') as f:
            f.write(self.editor.toPlainText())

        self.madeChanges = False

        self.emit(SIGNAL('currentFileNameChanged'))
        return True

    def saveFileAs(self):
        fpath = QFileDialog.getSaveFileName(self, 'Save As')
        if fpath == '':
            return False
        
        self.currentFilePath = fpath
        self.currentFileName = self.currentFilePath.split('/')[-1]
        self.firstSave = False

        with open(self.currentFilePath, 'w') as f:
            f.write(self.editor.toPlainText())

        self.madeChanges = False

        self.emit(SIGNAL('currentFileNameChanged'))
        return True

    def openPreferences(self):
        try:
            # Create the Preferences dialog
            dlg = preferences.PreferencesDlg(self)
            dlg.show()
            dlg.accepted.connect(self.updateUi)
        except Exception as e: # If failed to open Preferences dialog, just open the settings file
            self.currentFilePath = os.path.join(os.getcwd(), 'config/settings.ini')
            self.currentFileName = 'settings.ini'
            self.firstSave = False

            with open(self.currentFilePath, 'r') as f:
                self.editor.clear()
                self.editor.setText(f.read())

            self.emit(SIGNAL('currentFileNameChanged'))
            print(e)

    def closeFile(self):
        # Ask if want to save first, if changes have been made
        if self.madeChanges:
            reply = QMessageBox.question(self, "Save First?", 
            'You have unsaved changes. Would you like to save them before closing this file?',
                QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                if self.firstSave:
                    self.saveFileAs()
                else:
                    self.saveFile()
            elif reply == QMessageBox.Cancel:
                return

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
        cursor = self.editor.textCursor()
        cursor.setPosition(QTextCursor.Start)
        # cursor.selec/
        self.editor.selectAll()

    def comment(self):     
        # Get the cursor
        cursor = self.editor.textCursor()

        if cursor.hasSelection():
            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to end of selection
            cursor.setPosition(cursor.selectionEnd())

            # Get the range of selection
            diff = cursor.blockNumber() - temp

            # Iterate over lines 
            for i in range(diff + 1):
                # Move to the beginning of the line
                cursor.movePosition(QTextCursor.StartOfLine)

                # Is commented?
                if cursor.block().text().startswith(self.highlighter.commentChar):
                    # Remove comment char
                    cursor.deleteChar()
                else:
                    # Add comment char
                    cursor.insertText(self.highlighter.commentChar)

                # Move back up
                cursor.movePosition(QTextCursor.Up)
        else: # No selection, just toggle comment
            cursor.movePosition(QTextCursor.StartOfLine)

            if cursor.block().text().startswith(self.highlighter.commentChar):
                # Remove comment char
                cursor.deleteChar()
            else:
                # Add comment char
                cursor.insertText(self.highlighter.commentChar)

    def runWithPython2(self):
        # Save first
        if self.firstSave:
            if not self.saveFileAs():
                return
        else:
            if not self.saveFile():
                return

        try:
            python_path = self.settings['Python']['Python2Path'] + 'python'
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
        # Save first
        if self.firstSave:
            if not self.saveFileAs():
                return
        else:
            if not self.saveFile():
                return
            
        try:
            python_path = self.settings['Python']['Python3Path'] + 'python'
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
            if self.settings.getboolean('Editor', 'UseSpaces'):
                text = text.replace('\t', ' ' * self.settings.getint('Editor', 'SpacesPerTab'))
            else:
                text = text.replace(' ' * self.settings.getint('Editor', 'SpacesPerTab'), '\t')
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

    def indent(self):
        if self.settings.getboolean('Editor', 'UseSpaces'):
            indentation = ' ' * self.settings.getint('Editor', 'SpacesPerTab')
        else:
            indentation = '\t'
        
        # Get the cursor
        cursor = self.editor.textCursor()

        if cursor.hasSelection():
            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to end of selection
            cursor.setPosition(cursor.selectionEnd())

            # Get the range of selection
            diff = cursor.blockNumber() - temp

            # Iterate over lines 
            for i in range(diff + 1):
                # Move to the beginning of the line
                cursor.movePosition(QTextCursor.StartOfLine)

                # Tab
                cursor.insertText(indentation)

                # Move back up
                cursor.movePosition(QTextCursor.Up)
        else: # No selection, just indent
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.insertText(indentation)

    def dedent(self):
        cursor = self.editor.textCursor()

        if cursor.hasSelection():
            # Store current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's last line
            cursor.setPosition(cursor.selectionEnd())

            # Get range of selection
            diff = cursor.blockNumber() - temp

            # Iterate over lines
            for i in range(diff + 1):
                self.handleDedent(cursor)

                # Move up
                cursor.movePosition(QTextCursor.Up)
        else:
            self.handleDedent(cursor)

    def handleDedent(self, cursor):
        if self.settings.getboolean('Editor', 'UseSpaces'):
            indentation = ' ' * self.settings.getint('Editor', 'SpacesPerTab')
        else:
            indentation = '\t'

        cursor.movePosition(QTextCursor.StartOfLine)

        # get the current line
        line = cursor.block().text()

        # If the line starts with an indent, delete it 
        if line.startswith(indentation):
            for i in range(len(indentation)):
                cursor.deleteChar()

    def enter(self):
        """Smart Enter. Auto-Indents/Dedents (if enabled) appropriately"""
        # get cursor
        cursor = self.editor.textCursor()

        # Get current line
        line = cursor.block().text()

        # Get the current level of indentation
        if self.settings.getboolean('Editor', 'UseSpaces'):
            indentation = ' ' * self.settings.getint('Editor', 'SpacesPerTab')
        else:
            indentation = '\t'

        level = len(line.split(indentation)[:-1])

        # Insert new line
        cursor.insertText('\n')

        # Match current level of indentation
        for i in range(level):
            self.indent()

        # Strip indentation from line for parsing
        line = line.lstrip()

        # Should indent?
        for indenter in self.highlighter.indenters:
            if line.startswith(indenter):
                self.indent()
                return
        
        # Should dedent?
        for dedenter in self.highlighter.dedenters:
            if line.startswith(dedenter):
                self.dedent()
                return

    def backspace(self):
        """Smart backspace function to compliment the smart enter"""
        return
        if self.settings.getboolean('Editor', 'UseSpaces'):
            indentation = ' ' * self.settings.getint('Editor', 'SpacesPerTab')
        else:
            indentation = '\t'

        # get the cursor
        cursor = self.editor.textCursor()

        # Get current line
        line = cursor.block().text()

        # Check if need to deploy smart backspace action
        col = cursor.columnNumber()
        # if col != 0 and line[col - 1] 

    def quit(self):
        self.closeFile()
        qApp.quit()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyncilApp()
    window.show()
    sys.exit(app.exec_())