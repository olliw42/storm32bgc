#!/usr/bin/env python
#*******************************************************
# Copyright (c) OlliW42, STorM32 project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#*******************************************************

import sys
#import struct
#from math import sqrt, sin, pi
#from copy import deepcopy
import re
import os

###################################################################
# Main()
##################################################################
if __name__ == '__main__':

    print( "Hello, I'm ui2owpy\n" )

    if len(sys.argv)<2:
        print( "no file given as paramter\n" )
        sys.exit()

    fileName, fileExt = os.path.splitext(sys.argv[1])

    if fileExt != '':
        print( "file with extension not allowed\n" )
        sys.exit()


    if fileName.lower().endswith('_ui'):
        print( "file name must not end with _ui\n" )
        sys.exit()

    if fileName.lower().endswith('_qrc'):
        print( "file name must not end with _qrc\n" )
        sys.exit()

    '''
    fileNameQrc = fileName+'_qrc'
    try:
        F = open(fileNameQrc+'.qrc', "r")
    except IOError:
        pass
    else:
        F.close()
        print("calling qrc2py.bat "+fileNameQrc+"...")
        os.system( "pyrcc5 "+fileNameQrc+".qrc > "+fileNameQrc+"_rc.py" )
        print(fileNameQrc+"_rc.py created\n")
    '''

    fileNameUi = fileName+'_ui'
    try:
        F = open(fileNameUi+'.ui', "r")
    except IOError:
        print( "file "+fileNameUi+".ui does not exist\n" )
        sys.exit()
    else:
        F.close()

    print("calling ui2py.bat "+fileNameUi+"...")
    os.system( "pyuic5 "+fileNameUi+".ui -o "+fileNameUi+".py" )
    print(fileNameUi+".py created\n")

    F = open(fileNameUi+'.py', "r")
    fstr = F.read()
    F.close()

    print("converting "+fileNameUi+".py...")

    #replace all resize(800, 640)
    fstr = re.sub( r'resize\(([+\-\d]+?),[ ]*?([+\-\d]+)\)',
                   r'resize(self.SCALE(\1), self.SCALE(\2))',
                   fstr )

    #replace all QtCore.QSize(600, 300)
    fstr = re.sub( r'QtCore\.QSize\(([+\-\d]+?),[ ]*?([+\-\d]+)\)',
                   r'QtCore.QSize(self.SCALE(\1), self.SCALE(\2))',
                   fstr )

    #replace all QtCore.QRect(0, 0, 840, 22)
    fstr = re.sub( r'QtCore\.QRect\(([+\-\d]+?),[ ]*?([+\-\d]+),[ ]*?([+\-\d]+),[ ]*?([+\-\d]+)\)',
                   r'QtCore.QRect(self.SCALE(\1), self.SCALE(\2), self.SCALE(\3), self.SCALE(\4))',
                   fstr )

    #replace all setContentsMargins(0, 0, 0, 0)
    fstr = re.sub( r'setContentsMargins\(([+\-\d]+?),[ ]*?([+\-\d]+),[ ]*?([+\-\d]+),[ ]*?([+\-\d]+)\)',
                   r'setContentsMargins(self.SCALE(\1), self.SCALE(\2), self.SCALE(\3), self.SCALE(\4))',
                   fstr )

    #replace all setSpacing(0)
    fstr = re.sub( r'setSpacing\(([+\-\d]+?)\)',
                   r'setSpacing(self.SCALE(\1))',
                   fstr )

    #replace all QSpacerItem(5, 20,
    fstr = re.sub( r'QSpacerItem\(([+\-\d]+?),[ ]*?([+\-\d]+),',
                   r'QSpacerItem(self.SCALE(\1), self.SCALE(\2),',
                   fstr )

    #undo changes for 0
    fstr = re.sub( r'self\.SCALE\(0\)',
                   r'0',
                   fstr )

    #undo changes for 16777215
    fstr = re.sub( r'self\.SCALE\(16777215\)',
                   r'16777215',
                   fstr )

    #do intra changes
    fstr = re.sub( r'class Ui_wWindow\(object\):\n',
                   'class Ui_wWindow(object):\n'+
                   '    WINSCALE = 1.0\n\n'+
                   '    def SCALE(self, scale):\n'+
                   '        if( scale>=16777215 ): return scale\n'+
                   '        return int(self.WINSCALE*scale)\n\n',
                   fstr )

    fstr = re.sub( r'    def setupUi\(self, wWindow\):\n',
                   '    def setupUi(self, wWindow, winScale):\n'+
                   '        self.WINSCALE = winScale\n\n',
                   fstr )

    F = open(fileNameUi+'_ow.py', "w")
    F.write(fstr)
    F.close()

    print(fileNameUi+"_ow.py created")
    print('\nDONE')
