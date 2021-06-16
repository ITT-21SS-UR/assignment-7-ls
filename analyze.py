#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-
# Script was written by Michael Schmidt

'''
Start script with: analyze.py <PORT>
'''

import sys
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg


def get_port():
    if len(sys.argv) != 2:
        sys.stderr.write("Enter port number as first arugment!\n")
        sys.exit(1)

    return sys.argv[1]


if __name__ == '__main__':
    port = get_port()
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('DIPPID Graph')

    # Define a top-level widget to hold everything
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)

    #  Create a grid layout to manage the widgets size and position
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec_())
