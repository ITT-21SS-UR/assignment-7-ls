#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-
# Script was written by Michael Schmidt

"""
Script tkaes the DIPPID input and generates a
PyQtGraph for the x, y, z and rotation of the 
device. The rotation is shown via a normalvector.
The input values get logged via a LogNode and printed
to the stdout.
"""

import sys
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.flowchart import Flowchart, Node
import numpy as np
from DIPPID_pyqtnode import DIPPIDNode, BufferNode
import pyqtgraph.flowchart.library as fclib


class NormalVectorNode(Node):

    nodeName = "NormalVectorNode"

    def __init__(self, name):
        terminals = {
            "axis1": dict(io="in"),
            "axis2": dict(io="in"),
            "rotation": dict(io="out"),
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # negativ x axis for mirroring the vector for user perspective
        normal_vector = np.array(
            [[0, 0], [-kwds["axis1"][0], kwds["axis2"][0]]])
        return {"rotation": normal_vector}


class LogNode(Node):

    nodeName = "LogNode"

    def __init__(self, name):
        terminals = {
            "accelX": dict(io="in"),
            "accelY": dict(io="in"),
            "accelZ": dict(io="in"),
            "rotation": dict(io="in"),
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        x = kwds["accelX"][0]
        y = kwds["accelY"][0]
        z = kwds["accelZ"][0]
        rotation = kwds["rotation"]
        print(
            f"Acceleration X: {x}, Acceleration Y: {y}, Acceleration Z: {z}, Rotation: {rotation[1]}")


def init_normal_vector_plotting(layout, fc, dippid_node, log_node):
    # create normal vector plot widget
    plot_widget = pg.PlotWidget()
    layout.addWidget(plot_widget, 1, 1)
    plot_widget.setTitle("Normal Vector")
    plot_widget.setYRange(-1, 1)
    plot_widget.setXRange(-1, 1)

    # set plot widget nodes
    plot_widget_node = fc.createNode("PlotWidget", pos=(450, 100))
    plot_widget_node.setPlot(plot_widget)
    plot_normal_vector_node = fc.createNode(
        "NormalVectorNode", pos=(450, 200))

    # connect dippid
    fc.connectTerminals(dippid_node["accelX"],
                        plot_normal_vector_node["axis1"])
    fc.connectTerminals(dippid_node["accelY"],
                        plot_normal_vector_node["axis2"])
    fc.connectTerminals(
        plot_normal_vector_node["rotation"], plot_widget_node["In"])

    # connect normal vector to log
    fc.connectTerminals(
        plot_normal_vector_node["rotation"], log_node["rotation"])


def init_accel_plotting(layout, fc, dippid_node, log_node):
    inputs = ("accelX", "accelY", "accelZ")

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
        plot_widget_node = fc.createNode("PlotWidget", pos=(150, i * 100))
        plot_widget_node.setPlot(plot_widget)
        plot_widgets_nodes.append(plot_widget_node)

    # create buffer nodes
    buffer_nodes = []
    for i, plot_widget_node in enumerate(plot_widgets_nodes):
        buffer_node = fc.createNode("Buffer", pos=(300, i * 100))
        buffer_nodes.append(buffer_node)

    # connect dippid and log nodes
    for i, input in enumerate(inputs):
        fc.connectTerminals(dippid_node[input], buffer_nodes[i]["dataIn"])
        fc.connectTerminals(dippid_node[input], log_node[input])

    # connect buffer
    for i, buffer_node in enumerate(buffer_nodes):
        fc.connectTerminals(
            buffer_node["dataOut"], plot_widgets_nodes[i]["In"])


if __name__ == "__main__":
    fclib.registerNodeType(NormalVectorNode, [("Data",)])
    fclib.registerNodeType(LogNode, [("Data",)])
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle("DIPPID Graph")

    # Define a top-level widget to hold everything
    central_widget = QtGui.QWidget()
    win.setCentralWidget(central_widget)

    # Create a grid layout to manage the widgets size and position
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    # Creating flowchart
    fc = Flowchart(terminals={})
    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    # create DIPPID node
    dippid_node = fc.createNode("DIPPID", pos=(0, 0))

    # create log node
    log_node = fc.createNode("LogNode", pos=(600, 100))

    init_accel_plotting(layout, fc, dippid_node, log_node)
    init_normal_vector_plotting(layout, fc, dippid_node, log_node)

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        sys.exit(app.exec_())
