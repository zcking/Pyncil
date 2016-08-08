from PyQt4.QtCore import *
from PyQt4.QtGui import *
import configparser
import os

class PreferencesDlg(QDialog):
    def __init__(self, parent=None):
        super(PreferencesDlg, self).__init__(parent)

        self.loadConfig()

        self.makeWidgets()
        self.setInitialValues()
        self.makeConnections()
        self.setWindowTitle('Preferences')

        self.connect(self, SIGNAL('returnPressed()'), self.save)

    def loadConfig(self):
        self.config = None
        self.settings = None

        self.settings = configparser.ConfigParser()
        self.settings.read('config/settings.ini')
        try:
            self.theme = 'config/themes/' + self.themeBox.currentText() + '.ini'
        except:
            self.theme = ''
        if self.theme == '':
            self.theme = self.settings.get('Editor', 'theme', fallback='config/themes/default.ini')

        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.theme)
            self.settings['Editor']['theme'] = self.theme
        except:
            self.config.read('config/themes/default.ini') # Use the default color theme
            self.settings['Editor']['theme'] = self.theme

    def makeWidgets(self):
        self.mainLayout = QVBoxLayout()

        self.setupEditorWidgets()
        self.setupPythonWidgets()
        self.setupColorWidgets()
        self.setupExtensionsWidgets()

        buttonLayout = QHBoxLayout()
        self.saveButton = QPushButton('&Save')
        self.cancelButton = QPushButton('Cancel')
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)
        self.mainLayout.addLayout(buttonLayout)
        
        self.setLayout(self.mainLayout)

    def makeConnections(self):
        # Color Picker buttons
        self.bgButton.clicked.connect(self.selectBg)
        self.fgButton.clicked.connect(self.selectFg)
        self.singleButton.clicked.connect(self.selectSingle)
        self.multiButton.clicked.connect(self.selectMulti)
        self.stringButton.clicked.connect(self.selectString)
        self.keywordButton.clicked.connect(self.selectKeyword)
        self.functionButton.clicked.connect(self.selectFunction)
        self.highlightButton.clicked.connect(self.selectHighlight)
        self.highlightedTextButton.clicked.connect(self.selectHighlightedText)

        # Accept/Cancel buttons
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.cancel)

    def getThemes(self):
        """Parse through the theme dir and get the themes names as strings.
        Returns a list (of theme names)."""
        themes = []
        for file in os.listdir('config/themes/'):
            if file.endswith('.ini'):
                themes.append(file[:-4])
        return themes

    def setColorValues(self):
        # Get the theme
        self.loadConfig()

        # Set the widget values
        self.bgInput.setText(self.config['Colors']['Background'])
        self.fgInput.setText(self.config['Colors']['Foreground'])
        self.singleInput.setText(self.config['Colors']['SingleLineComment'])
        self.multiInput.setText(self.config['Colors']['MultiLineComment'])
        self.stringInput.setText(self.config['Colors']['String'])
        self.keywordInput.setText(self.config['Colors']['Keyword'])
        self.functionInput.setText(self.config['Colors']['Function'])
        self.highlightInput.setText(self.config['Colors']['Highlight'])
        self.highlightedTextInput.setText(self.config['Colors']['HighlightedText'])

    def themeSelected(self):
        # Theme has been selected, now update the other theme setting widgets
        # to contain *that* theme's colors
        self.setColorValues()

    def setupEditorWidgets(self):
        # Editor widgets
        self.fontBox = QLineEdit()
        self.fontSize = QSpinBox()
        self.fontSize.setRange(4, 72)
        self.fixedPitchToggle = QCheckBox('Fixed Pitch')
        self.wordSpacing = QDoubleSpinBox()
        self.wordSpacing.setRange(0.5, 5.0)
        self.useSpaces = QCheckBox('Use Spaces')
        self.spacesPerTab = QSpinBox()
        self.spacesPerTab.setRange(1, 8)
        self.showLineNumbers = QCheckBox('Show Line Numbers')
        self.smartIndent = QCheckBox('Smart Indent')
        self.themeBox = QComboBox()
        themes = self.getThemes()
        self.themeBox.addItems(themes)
        self.themeBox.setCurrentIndex(themes.index(self.settings['Editor']['theme'].split('/')[-1][:-4])) # Set the current item to the the current theme (without the path and .ini part)
        self.themeBox.activated.connect(self.themeSelected)

        # Editor Group
        self.editorLayout = QGridLayout()
        self.editorLayout.addWidget(QLabel('Font:'), 0, 0)
        self.editorLayout.addWidget(self.fontBox, 0, 1)
        self.editorLayout.addWidget(QLabel('Font Size:'), 1, 0)
        self.editorLayout.addWidget(self.fontSize, 1, 1)
        self.editorLayout.addWidget(self.fixedPitchToggle, 2, 0, 1, 2)
        self.editorLayout.addWidget(QLabel('Word Spacing:'), 3, 0)
        self.editorLayout.addWidget(self.wordSpacing, 3, 1)
        self.editorLayout.addWidget(self.useSpaces, 4, 0)
        self.editorLayout.addWidget(QLabel('Spaces Per Tab:'), 5, 0)
        self.editorLayout.addWidget(self.spacesPerTab, 5, 1)
        self.editorLayout.addWidget(self.showLineNumbers, 6, 0)
        self.editorLayout.addWidget(self.smartIndent, 7, 0)
        self.editorLayout.addWidget(QLabel('Theme:'), 8, 0)
        self.editorLayout.addWidget(self.themeBox, 8, 1)

        self.editorGroupBox = QGroupBox('Editor')
        self.editorGroupBox.setLayout(self.editorLayout)
        self.mainLayout.addWidget(self.editorGroupBox)

    def setupPythonWidgets(self):
        # Python widgets
        self.py2path = QLineEdit()
        self.py3path = QLineEdit()

        # Python Group
        self.pythonLayout = QGridLayout()
        self.pythonLayout.addWidget(QLabel('Python 2 Path:'), 0, 0, 1, 2)
        self.pythonLayout.addWidget(self.py2path, 1, 0, 1, 2)
        self.pythonLayout.addWidget(QLabel('Python 3 Path:'), 2, 0, 1, 2)
        self.pythonLayout.addWidget(self.py3path, 3, 0, 1, 2)

        self.pythonGroupBox = QGroupBox('Python')
        self.pythonGroupBox.setLayout(self.pythonLayout)
        self.mainLayout.addWidget(self.pythonGroupBox)

    def setupColorWidgets(self):
        # Color widgets
        self.bgInput = QLineEdit()
        self.bgButton = QPushButton('Choose...')
        self.fgInput = QLineEdit()
        self.fgButton = QPushButton('Choose...')
        self.singleInput = QLineEdit()
        self.singleButton = QPushButton('Choose...')
        self.multiInput = QLineEdit()
        self.multiButton = QPushButton('Choose...')
        self.stringInput = QLineEdit()
        self.stringButton = QPushButton('Choose...')
        self.keywordInput = QLineEdit()
        self.keywordButton = QPushButton('Choose...')
        self.functionInput = QLineEdit()
        self.functionButton = QPushButton('Choose...')
        self.highlightInput = QLineEdit()
        self.highlightButton = QPushButton('Choose...')
        self.highlightedTextInput = QLineEdit()
        self.highlightedTextButton = QPushButton('Choose...')

        # Color layout
        self.colorLayout = QGridLayout()
        self.colorLayout.addWidget(QLabel('Background:'), 0, 0)
        self.colorLayout.addWidget(self.bgInput, 0, 1)
        self.colorLayout.addWidget(self.bgButton, 0, 2)
        self.colorLayout.addWidget(QLabel('Foreground:'), 1, 0)
        self.colorLayout.addWidget(self.fgInput, 1, 1)
        self.colorLayout.addWidget(self.fgButton, 1, 2)
        self.colorLayout.addWidget(QLabel('Single Line Comment:'), 2, 0)
        self.colorLayout.addWidget(self.singleInput, 2, 1)
        self.colorLayout.addWidget(self.singleButton, 2, 2)
        self.colorLayout.addWidget(QLabel('Mult-Line Comment:'), 3, 0)
        self.colorLayout.addWidget(self.multiInput, 3, 1)
        self.colorLayout.addWidget(self.multiButton, 3, 2)
        self.colorLayout.addWidget(QLabel('String:'), 4, 0)
        self.colorLayout.addWidget(self.stringInput, 4, 1)
        self.colorLayout.addWidget(self.stringButton, 4, 2)
        self.colorLayout.addWidget(QLabel('Keyword:'), 5, 0)
        self.colorLayout.addWidget(self.keywordInput, 5, 1)
        self.colorLayout.addWidget(self.keywordButton, 5, 2)
        self.colorLayout.addWidget(QLabel('Function:'), 6, 0)
        self.colorLayout.addWidget(self.functionInput, 6, 1)
        self.colorLayout.addWidget(self.functionButton, 6, 2)
        self.colorLayout.addWidget(QLabel('Highlight:'), 7, 0)
        self.colorLayout.addWidget(self.highlightInput, 7, 1)
        self.colorLayout.addWidget(self.highlightButton, 7, 2)
        self.colorLayout.addWidget(QLabel('Highlighted Text:'), 8, 0)
        self.colorLayout.addWidget(self.highlightedTextInput, 8, 1)
        self.colorLayout.addWidget(self.highlightedTextButton, 8, 2)

        # Color Group
        self.colorGroupBox = QGroupBox('Colors')
        self.colorGroupBox.setLayout(self.colorLayout)
        self.mainLayout.addWidget(self.colorGroupBox)

    def setupExtensionsWidgets(self):
        # Extensions Widgets
        self.highlighter = QLineEdit()

        # Extensions Layout
        self.extensionsLayout = QGridLayout()
        self.extensionsLayout.addWidget(QLabel('Highlighter Class:'))
        self.extensionsLayout.addWidget(self.highlighter)

        # Extensions Group
        self.extensionsGroupBox = QGroupBox('Extensions')
        self.extensionsGroupBox.setLayout(self.extensionsLayout)
        self.mainLayout.addWidget(self.extensionsGroupBox)

    def setInitialValues(self):
        self.fontBox.setText(self.settings['Editor']['Font'])
        self.fontSize.setValue(self.settings.getint('Editor', 'FontSize'))
        self.fixedPitchToggle.setChecked(self.settings.getboolean('Editor', 'FixedPitch'))
        self.wordSpacing.setValue(self.settings.getfloat('Editor', 'WordSpacing'))
        self.useSpaces.setChecked(self.settings.getboolean('Editor', 'UseSpaces'))
        self.spacesPerTab.setValue(self.settings.getint('Editor', 'SpacesPerTab'))
        self.showLineNumbers.setChecked(self.settings.getboolean('Editor', 'ShowLineNumbers'))
        self.smartIndent.setChecked(self.settings.getboolean('Editor', 'smartindent'))

        self.py2path.setText(self.settings['Python']['Python2Path'])
        self.py3path.setText(self.settings['Python']['Python3Path'])

        self.bgInput.setText(self.config['Colors']['Background'])
        self.fgInput.setText(self.config['Colors']['Foreground'])
        self.singleInput.setText(self.config['Colors']['SingleLineComment'])
        self.multiInput.setText(self.config['Colors']['MultiLineComment'])
        self.stringInput.setText(self.config['Colors']['String'])
        self.keywordInput.setText(self.config['Colors']['Keyword'])
        self.functionInput.setText(self.config['Colors']['Function'])
        self.highlightInput.setText(self.config['Colors']['Highlight'])
        self.highlightedTextInput.setText(self.config['Colors']['HighlightedText'])

        self.highlighter.setText(self.settings['Extensions']['Highlighter'])

    def getValues(self):
        """Reads the values from the preference widgets and 
        stores them in the self.settings and self.config ConfigParser object."""
        # Get correct config/theme
        self.loadConfig()

        self.settings.set('Editor', 'Font', self.fontBox.text())
        self.settings.set('Editor', 'FontSize', str(self.fontSize.value()))
        temp = 'yes' if self.fixedPitchToggle.isChecked() else 'no'
        self.settings.set('Editor', 'FixedPitch', temp)
        self.settings.set('Editor', 'WordSpacing', str(self.wordSpacing.value()))
        temp = 'yes' if self.useSpaces.isChecked() else 'no'
        self.settings.set('Editor', 'UseSpaces', temp)
        self.settings.set('Editor', 'SpacesPerTab', str(self.spacesPerTab.value()))
        temp = 'yes' if self.showLineNumbers.isChecked() else 'no'
        self.settings.set('Editor', 'ShowLineNumbers', temp)
        temp = 'yes' if self.smartIndent.isChecked() else 'no'
        self.settings.set('Editor', 'smartindent', temp)
        self.settings.set('Editor', 'theme', 'config/themes/' + self.themeBox.currentText() + '.ini')

        self.settings.set('Python', 'Python2Path', self.py2path.text())
        self.settings.set('Python', 'Python3Path', self.py3path.text())

        self.config.set('Colors', 'Background', self.bgInput.text())
        self.config.set('Colors', 'Foreground', self.fgInput.text())
        self.config.set('Colors', 'SingleLineComment', self.singleInput.text())
        self.config.set('Colors', 'MultiLineComment', self.multiInput.text())
        self.config.set('Colors', 'String', self.stringInput.text())
        self.config.set('Colors', 'Keyword', self.keywordInput.text())
        self.config.set('Colors', 'Function', self.functionInput.text())
        self.config.set('Colors', 'Highlight', self.highlightInput.text())
        self.config.set('Colors', 'HighlightedText', self.highlightedTextInput.text())

        self.settings.set('Extensions', 'Highlighter', self.highlighter.text())

    def makeColorDlg(self, lineedit):
        colorDlg = QColorDialog(self)
        colorDlg.setCurrentColor(QColor('#' + lineedit.text()))
        colorDlg.show()

        def update():
            color = colorDlg.currentColor()
            rVal, gVal, bVal, aVal = color.getRgb()
            # Pad the hex string, if needed
            colorString = ''
            if rVal < 0x0F:
                colorString += '0'
            colorString += '%x' % rVal
            if gVal < 0x0F:
                colorString += '0'
            colorString += '%x' % gVal
            if bVal < 0x0F:
                colorString += '0'
            colorString += '%x' % bVal
            lineedit.setText(colorString)
        colorDlg.accepted.connect(update)

    def selectBg(self):
        self.makeColorDlg(self.bgInput)

    def selectFg(self):
        self.makeColorDlg(self.fgInput)

    def selectSingle(self):
        self.makeColorDlg(self.singleInput)

    def selectMulti(self):
        self.makeColorDlg(self.multiInput)

    def selectString(self):
        self.makeColorDlg(self.stringInput)

    def selectKeyword(self):
        self.makeColorDlg(self.keywordInput)

    def selectFunction(self):
        self.makeColorDlg(self.functionInput)

    def selectHighlight(self):
        self.makeColorDlg(self.highlightInput)

    def selectHighlightedText(self):
        self.makeColorDlg(self.highlightedTextInput)

    def save(self):
        # Get values into self.config
        self.getValues()

        # save the config to file
        with open('config/settings.ini', 'w') as f:
            self.settings.write(f)
        # save the config to file
        with open(self.settings['Editor']['theme'], 'w') as f:
            self.config.write(f)

        self.emit(SIGNAL('preferencesUpdated'))

        self.accept()

        # close the dialog
        self.destroy()
    
    def cancel(self):
        self.reject()
        self.destroy()