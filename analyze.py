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
from pyqtgraph.flowchart import Flowchart, Node
import numpy as np


def plot_accels(layout):
    fc = Flowchart(terminals={})
    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    inputs = ("acceleration_x", "acceleration_y", "acceleration_z")

    for i, input in enumerate(inputs):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle(input.title())
        plot_widget.setYRange(-1, 1)
        layout.addWidget(plot_widget, 0, i + 1)
        plot_widget_node = fc.createNode('PlotWidget', pos=(300, i * 100))
        plot_widget_node.setPlot(plot_widget)


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
    central_widget = QtGui.QWidget()
    win.setCentralWidget(central_widget)

    #  Create a grid layout to manage the widgets size and position
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    plot_accels(layout)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec_())
