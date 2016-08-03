from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

import re

class Find(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        
        self.lastMatch = None
        self.initUI()

    def initUI(self):
        # Search button
        findButton = QtGui.QPushButton('Find', self)
        findButton.clicked.connect(self.find)
        self.connect(findButton, QtCore.SIGNAL('returnPressed()'), self.find)

        # Replace Button
        replaceButton = QtGui.QPushButton('Replace', self)
        replaceButton.clicked.connect(self.replace)
        self.connect(replaceButton, QtCore.SIGNAL('returnPressed()'), self.replace)

        # Replace All Button
        replaceAllButton = QtGui.QPushButton('Replace All', self)
        replaceAllButton.clicked.connect(self.replaceAll)

        # Normal Mode
        self.normalRadio = QtGui.QRadioButton('Normal', self)
        self.normalRadio.toggled.connect(self.normalMode)

        # Regex Mode
        self.regexRadio = QtGui.QRadioButton('RegEx', self)
        self.regexRadio.toggled.connect(self.regexMode)

        # Search input
        self.findField = QtGui.QLineEdit(self)

        # Replace input
        self.replaceField = QtGui.QLineEdit(self)

        optionsLabel = QtGui.QLabel('Options: ', self)

        # Case sensitivity option
        self.caseSensitive = QtGui.QCheckBox('Case sensitive', self)

        # Whole words option
        self.wholeWords = QtGui.QCheckBox('Whole words', self)

        # Layout
        layout = QtGui.QGridLayout()
        layout.addWidget(self.findField, 1, 0, 1, 4)
        layout.addWidget(self.normalRadio, 2, 2)
        layout.addWidget(self.regexRadio, 2, 3)
        layout.addWidget(findButton, 2, 0, 1, 2)
        layout.addWidget(self.replaceField, 3, 0, 1, 4)
        layout.addWidget(replaceButton, 4, 0, 1, 2)
        layout.addWidget(replaceAllButton, 4, 2, 1, 2)

        spacer = QtGui.QWidget(self)
        spacer.setFixedSize(0, 10)
        layout.addWidget(spacer, 5, 0)
        
        layout.addWidget(optionsLabel, 6, 0)
        layout.addWidget(self.caseSensitive, 6, 1)
        layout.addWidget(self.wholeWords, 6, 2)

        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle('Find and Replace')
        self.setLayout(layout)

        # Normal mode by default
        self.normalRadio.setChecked(True)

    def find(self):
        # Get text
        text = self.parent.editor.toPlainText()

        # And text to Find
        query = self.findField.text()

        if self.wholeWords.isChecked():
            query = r'\W' + query + r'\W'

        # By default regexes are case sensitive but usually a search isn't
        flags = 0 if self.caseSensitive.isChecked() else re.I

        # Compile the pattern
        pattern = re.compile(query, flags)

        # use last match position, if available
        start = self.lastMatch.start() + 1 if self.lastMatch else 0

        # The actual search
        self.lastMatch = pattern.search(text, start)

        if self.lastMatch:
            start = self.lastMatch.start()
            end = self.lastMatch.end()

            # If using whole words, include the two non-alphanumerics wrapping it 
            if self.wholeWords.isChecked():
                start += 1
                end -= 1

            self.moveCursor(start, end)
        else:
            # set the cursor to the end if search failed
            self.parent.editor.moveCursor(QtGui.QTextCursor.End)

    def replace(self):
        # Get cursor
        cursor = self.parent.editor.textCursor()

        # Security
        if self.lastMatch and cursor.hasSelection():
            # Insert the new text, which will override the selected text
            cursor.insertText(self.replaceField.text())

            # And set the new cursor
            self.parent.editor.setTextCursor(cursor)

    def replaceAll(self):
        # Set lastmatch to None so the search starts from the beginning
        self.lastMatch = None

        # Initial find() call so that lastMatch is potentially not None 
        self.find()

        # Replace and find until find is None again
        while self.lastMatch:
            self.replace()
            self.find()

    def regexMode(self):
        # First uncheck the checkboxes
        self.caseSensitive.setChecked(False)
        self.wholeWords.setChecked(False)

        # Then disable them 
        self.caseSensitive.setEnabled(False)
        self.wholeWords.setEnabled(False)

    def normalMode(self):
        # Enable checkboxes
        self.caseSensitive.setEnabled(True)
        self.wholeWords.setEnabled(True)

    def moveCursor(self, start, end):
        # Get the QTextCursor object from parent's QTextEdit
        cursor = self.parent.editor.textCursor()

        # Then set position to beginning of last match
        cursor.setPosition(start)

        # Move the Cursor over the match and pass KeepAnchor to select the text
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)

        # And finally, set this new cursor as the parent's
        self.parent.editor.setTextCursor(cursor)