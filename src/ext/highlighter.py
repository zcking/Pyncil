from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
import configparser

# For extending Pyncil with your own highlighter class, say for C++,
# Simple add the class to this file and have it subclass from BaseHighlighter.
# You can use the PythonHighlighter for reference.
# Keep in mind that the QtWidget acting as the parent of the highlighter will always
# be the QTextEdit in the PyncilApp, stored in the instance variable 'editor'
# so if you keep a reference to the parent (the QTextEdit) as self.parent, you can reference it with 
# self.parent.editor.

# After creating your own highlighter class, simply change the configuration for Extensions -> Highlighter 
# to the name of your class.

class BaseHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(BaseHighlighter, self).__init__(parent)

        self.parent = parent

        def getPalette(self):
            raise NotImplementedError('You must subclass BaseHighlighter and implement this function. It should return a QtGui.QPalette.')


class PythonHighlighter(BaseHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.parent = parent
        self.loadConfig()

        self.classRegex = QtCore.QRegExp("\\bQ[A-Za-z]+\\b")
        self.singleLineCommentRegex = QtCore.QRegExp("#[^\n]*")
        self.multiLineCommentRegex = None
        self.singleQuoteRegex = QtCore.QRegExp("'.*'")
        self.doubleQuoteRegex = QtCore.QRegExp("\".*\"")
        self.functionRegex = QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()")
        self.commentStartRegex = QtCore.QRegExp('/"""')
        self.commentEndRegex = QtCore.QRegExp('"""/')

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        self.keywordPatterns = self.getPatterns('ext/python_keywords.txt')
        self.highlightingRules =[(QtCore.QRegExp(pattern), keywordFormat)
                for pattern in self.keywordPatterns]

        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append((self.classRegex, 
            classFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        self.highlightingRules.append((self.singleLineCommentRegex, singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()

        quotationFormat = QtGui.QTextCharFormat()
        self.highlightingRules.append((self.doubleQuoteRegex,
            quotationFormat))
        self.highlightingRules.append((self.singleQuoteRegex,
            quotationFormat))

        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules.append((self.functionRegex,
            functionFormat))

        self.commentStartExpression = self.commentStartRegex
        self.commentEndExpression = self.commentEndRegex

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)

    def getPatterns(self, filepath):
        patterns = []
        with open(filepath, 'r') as f:
            for keyword in f:
                patterns.append('\\b{}\\b'.format(keyword.strip()))
        return patterns

    def loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/settings.ini')

    def getQColor(self, colorString):
        try:
            # Assume the string is hexadecimal RGB
            rVal = int(colorString[:2], 16)
            gVal = int(colorString[2:4], 16)
            bVal = int(colorString[4:6], 16)
            return QtGui.QColor(rVal, gVal, bVal)
        except:
            # Not hex string, so try a built-in QColor color
            try:
                return QtGui.QColor(colorString)
            except:
                return None

    def getPalette(self):
        palette = QtGui.QPalette()

        # Keywords
        keywordColor = self.getQColor(self.config['Colors']['Keyword'])
        if keywordColor:
            keywordFormat = QtGui.QTextCharFormat()
            keywordFormat.setForeground(keywordColor)
            self.highlightingRules += [(pattern, keywordFormat) for pattern in self.keywordPatterns]
        else:
            self.makeErrorPopup(msg='Unable to load the color for Keyword from settings')

        # Background Color
        bgColor = self.getQColor(self.config['Colors']['Background'])
        if bgColor:
            palette.setColor(QtGui.QPalette.Base, bgColor)
        else:
            self.makeErrorPopup(msg='Unable to load the color for Background from settings')

        # Foreground Color
        fgc = self.getQColor(self.config['Colors']['Foreground'])
        if fgc:
            palette.setColor(QtGui.QPalette.Text, fgc)
        else:
            self.makeErrorPopup(msg='Unable to load the color for Foreground from settings')

        # Single Line Comments
        lineCommentColor = self.getQColor(self.config['Colors']['SingleLineComment'])
        if lineCommentColor:
            lineCommentFormat = QtGui.QTextCharFormat()
            lineCommentFormat.setForeground(lineCommentColor)
            self.highlightingRules.append((self.singleLineCommentRegex, lineCommentFormat))
        else:
            self.makeErrorPopup(msg='Unable to load the color for SingleLineComment from settings')

        # Block Comment
        # blockCommentFormat = QtGui.QTextCharFormat()
        # blockCommentFormat.setForeground(self.getQColor(self.config['Colors']['MultiLineComment']))
        # self.highlightingRules.append((self.multiLineCommentRegex, blockCommentFormat))

        # Single Quotes
        singleQuoteColor = self.getQColor(self.config['Colors']['String'])
        if singleQuoteColor:
            singleQuoteFormat = QtGui.QTextCharFormat()
            singleQuoteFormat.setForeground(singleQuoteColor)
            self.highlightingRules.append((self.singleQuoteRegex, singleQuoteFormat))
        else:
            self.makeErrorPopup(msg='Unable to load the color for String from settings')

        # Double Quotes (uses same as single quote string)
        if singleQuoteColor:
            singleQuoteFormat = QtGui.QTextCharFormat()
            singleQuoteFormat.setForeground(singleQuoteColor)
            self.highlightingRules.append((self.doubleQuoteRegex, singleQuoteFormat))

        # Functions
        functionColor = self.getQColor(self.config['Colors']['Function'])
        if functionColor:
            functionFormat = QtGui.QTextCharFormat()
            functionFormat.setForeground(functionColor)
            self.highlightingRules.append((self.functionRegex, functionFormat))
        else:
            self.makeErrorPopup(msg='Unable to load the color for Function from settings')

        selectColor = self.getQColor(self.config['Colors']['Highlight'])
        if selectColor:
            palette.setColor(QtGui.QPalette.Highlight, selectColor)
        else:
            self.makeErrorPopup(msg='Unable to load the color for Highlight from settings')

        selectedTextColor = self.getQColor(self.config['Colors']['HighlightedText'])
        if selectedTextColor:
            palette.setColor(QtGui.QPalette.HighlightedText, selectedTextColor)
        else:
            self.makeErrorPopup(msg='Unable to load the color for HighlightedText from settings')

        return palette

    def makeErrorPopup(self, title='Oops', msg='Something went wrong...'):
        popup = QtGui.QErrorMessage(self)
        popup.setWindowTitle(title)
        popup.showMessage(msg)