from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
import configparser


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        self.classRegex = QtCore.QRegExp("\\bQ[A-Za-z]+\\b")
        self.singleLineCommentRegex = QtCore.QRegExp("#[^\n]*")
        self.multiLineCommentRegex = None
        self.singleQuoteRegex = QtCore.QRegExp("'.*'")
        self.doubleQuoteRegex = QtCore.QRegExp("\".*\"")
        self.functionRegex = QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()")
        self.commentStartRegex = QtCore.QRegExp('/"""')
        self.commentEndRegex = QtCore.QRegExp('"""/')

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.magenta)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywordPatterns = self.getPatterns('ext/python_keywords.txt')

        self.highlightingRules =[(QtCore.QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]

        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        classFormat.setForeground(QtCore.Qt.darkMagenta)
        self.highlightingRules.append((self.classRegex, 
            classFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.red)
        self.highlightingRules.append((self.singleLineCommentRegex, singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QtCore.Qt.red)

        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtCore.Qt.darkGreen)
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