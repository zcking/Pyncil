import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
buildOptions = {"packages": [
	'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.phonon', 'sys', 'os', 'configparser', 'multiprocessing', 'webbrowser', 'tempfile', 'traceback'],
	 "excludes": ["tkinter"], "include_files": []}


# GUI applications require a different base on Windows
# the default is for a console application
base = 'Win32GUI' if sys.platform == "win32" else None

setup( 	name = "Pyncil",
	 	version = "1.0.0",
	 	description = "An extendible, configurable text editor created by Zachary King",
	 	options = {"build_exe": buildOptions},
	 	executables = [Executable("pyncil.pyw", base=base)])
