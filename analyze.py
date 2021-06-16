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
from DIPPID_pyqtnode import DIPPIDNode, BufferNode


def init_plotting(layout, fc):
    inputs = ("accelX", "accelY", "accelZ")

    # create DIPPID node
    dippid_node = fc.createNode("DIPPID", pos=(0, -100))

    # create plot widgets
    plot_widgets = []
    for i, input in enumerate(inputs):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle(input.title())
        plot_widget.setYRange(-1, 1)
        layout.addWidget(plot_widget, 0, i + 1)
        plot_widgets.append(plot_widget)

    # set plot widget nodes
    plot_widgets_nodes = []
    for i, plot_widget in enumerate(plot_widgets):
        plot_widget_node = fc.createNode('PlotWidget', pos=(150, i * 100))
        plot_widget_node.setPlot(plot_widget)
        plot_widgets_nodes.append(plot_widget_node)

    # create buffer nodes
    buffer_nodes = []
    for i, plot_widget_node in enumerate(plot_widgets_nodes):
        buffer_node = fc.createNode('Buffer', pos=(300, i * 100))
        buffer_nodes.append(buffer_node)

    # connect dippid
    for i, input in enumerate(inputs):
        # print(input)
        # print(buffer_nodes[i])
        fc.connectTerminals(dippid_node[input], buffer_nodes[i]['dataIn'])

    # connect buffer
    for i, buffer_node in enumerate(buffer_nodes):
        fc.connectTerminals(
            buffer_node['dataOut'], plot_widgets_nodes[i]['In'])


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

    # Create a grid layout to manage the widgets size and position
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    # Creating flowchart
    fc = Flowchart(terminals={'out': dict(io='out')})
    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    init_plotting(layout, fc)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec_())
