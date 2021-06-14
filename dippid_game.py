#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# This script was written by Johannes Lorper
import random

from DIPPID import SensorUDP
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QLabel
import sys
from PyQt5.QtGui import QPixmap


class DippidGame(QtWidgets.QWidget):
    def __init__(self, participantid=0):
        super().__init__()
        self.dippid = None
        self._acc_val_x = 0
        self.update_rate = 20  # updates per second

        self.__ui = uic.loadUi("dippid_game.ui", self)
        self._init_ui()
        self._player_icon = self.__ui.PlayerIcon
        self._add_image_to_label(self._player_icon, "dog-2835088_640.png")
        self._game_frame = self.__ui.GameFrame
        self._current_player_position_x = self._player_icon.x()
        self._player_width = self._player_icon.frameGeometry().width()
        self._current_player_position_y = self._player_icon.y()
        self.show()
        self.hide()
        self._start_frame_geometry = self._game_frame.frameGeometry()
        self._current_frame_geometry = self._start_frame_geometry
        self._standard_translation_rate = -15  # rate on which the accelerator value get translated into pixels
        self._current_score = 0
        self._lcd_score_screen = self.__ui.ScoreScreen

        self._drop_amount = 5
        self._drop_height = 100
        self._drop_width = 100
        self._min_drop_speed = 1
        self._max_drop_speed = 5
        self._drop_list = []
        self._create_new_drops(self._drop_amount)
        self._is_game_running = False
        self.show()


    def _add_image_to_label(self, label, imageName):
        image = QPixmap(imageName)
        resized_image = image.scaled(label.geometry().width(), label.geometry().height(), QtCore.Qt.KeepAspectRatio)
        label.setPixmap(resized_image)
        label.setStyleSheet("QLabel{ background-color: transparent;}")

    def _init_ui(self):
        self.connect_button = self.__ui.ConnectButton
        self.port_line_edit = self.__ui.PortLineEdit
        self.connect_button.clicked.connect(self.connect_dippid)
        self.start_button = self.__ui.StartButton
        self.start_button.clicked.connect(self.start_or_pause_game)
        self.explanation_label = self.__ui.ExplanationLabel

        """self.dippid = None
        self.port = "5700"
        self.dippid = SensorUDP(int(self.port.strip()))
       """

    def connect_dippid(self):
        print("button pressed")
        if self.connect_button.text() != "Connect" and self.connect_button.text() != "try again":
            return

        self.connect_button.setText("connecting...")
        self.dippid = SensorUDP(int(self.port_line_edit.text().strip()))

        if self.dippid is None:
            self.connect_button.setText("try again")
            return

        self.connect_button.setText("connected")
        self.connect_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def start_or_pause_game(self):
        if not self._is_game_running:
            self.update_timer = QtCore.QTimer()
            self.set_update_rate(self.update_rate)
            self.update_timer.timeout.connect(self.update_game)
            self.start_button.setText("Pause")
            self.explanation_label.setHidden(True)
            self._is_game_running = True
        else:
            self.update_timer.stop()
            self.start_button.setText("Resume")
            self.explanation_label.setHidden(False)
            self._is_game_running = False

    def _create_new_drops(self, amount):
        for i in range(amount):
            new_drop = QLabel("drop", self._game_frame )
            drop_x = random.randint(0, self._current_frame_geometry.width())
            new_drop.setGeometry(drop_x, 0-self._drop_height, self._drop_width, self._drop_height)
            print(new_drop.geometry())
            # Image from : https://upload.wikimedia.org/wikipedia/commons/7/79/Water_Drop_Icon_Vector.png
            self._add_image_to_label(new_drop, "Water_Drop_Icon_Vector.png")
            new_drop_speed = random.randint(self._min_drop_speed, self._max_drop_speed)
            self._drop_list.append((new_drop, new_drop_speed))



    def update_game(self):
        if self.dippid is None or not self.dippid.has_capability('accelerometer'):
            return

        v = self.dippid.get_value('accelerometer')
        self._acc_val_x = v['x']
        self.move_player(self._acc_val_x)
        self.move_drops()

        self.update()

    def set_update_rate(self, rate):

        if self.dippid is None:
            return

        if rate == 0:
            self.update_timer.stop()
        else:
            self.update_timer.start(int(1000 / rate))

    def update_score(self, score):
        self._current_score += score
        self._lcd_score_screen.display(self._current_score)

    def move_player(self, acc_x_value):
        x_move_value = self._standard_translation_rate*acc_x_value

        # Don't let the player icon x coordinate get bigger than the frame end
        if self._current_player_position_x + self._player_width + x_move_value > self._current_frame_geometry.width():
            self._current_player_position_x = self._current_frame_geometry.width() - self._player_width
        # Don't let the player icon x coordinate get smaller than 0
        elif self._current_player_position_x + x_move_value < 0:
            self._current_player_position_x = 0
        else:
            self._current_player_position_x += x_move_value

        self._player_icon.move(int(self._current_player_position_x), int(self._current_player_position_y))

    def move_drops(self):
        for drop, speed in self._drop_list:
            drop.move(drop.x(), drop.y()+speed)
            if drop.y() > self._current_frame_geometry.height():
                drop_x = random.randint(0, self._current_frame_geometry.width())
                drop.setGeometry(drop_x, 0-self._drop_height, self._drop_width, self._drop_height)
                self.update_score(-10)
            if drop.geometry().intersects(self._player_icon.geometry()):
                drop_x = random.randint(0, self._current_frame_geometry.width())
                drop.setGeometry(drop_x, 0-self._drop_height, self._drop_width, self._drop_height)
                self.update_score(10)





    def resizeEvent(self, event):
        self._current_frame_geometry = self._game_frame.frameGeometry()
        self._current_player_position_y = self._current_frame_geometry.height()-self._player_icon.frameGeometry().height()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dippidGame = DippidGame()
    sys.exit(app.exec_())

