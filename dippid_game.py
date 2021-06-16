#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# This script was written by Johannes Lorper
# fruit images from https://pixabay.com/de/illustrations/
# fr%c3%bcchte-banane-orange-apple-papaya-3658159/
# basket image from https://pixabay.com/de/vectors/
# korb-picknick-brown-griffe-objekt-310061/
import random

from DIPPID import SensorUDP
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QLabel
import sys
from PyQt5.QtGui import QPixmap


class DippidGame(QtWidgets.QWidget):
    def __init__(self, port="5700"):
        super().__init__()
        self.chosen_port = port
        self.dippid = None
        self._acc_val_x = 0
        # rate at which accelerometer data gets refreshed
        self.sensor_update_rate_per_s = 20
        self.sensor_update_timer = QtCore.QTimer()
        self.sensor_update_timer.timeout.connect(self.update_sensor_data)

        self.graphics_update_rate_per_s = 20
        self.graphics_update_timer = QtCore.QTimer()
        self.graphics_update_timer.timeout.connect(self.update_game)

        self.__ui = uic.loadUi("dippid_game.ui", self)
        self._init_ui()
        self._player_icon = self.__ui.PlayerIcon
        self._player_types_list = [
            {"type": "pineapple", "image": "pineapple_basket.png"},
            {"type": "apple", "image": "apple_basket.png"},
            {"type": "banana", "image": "banana_basket.png"}
        ]
        self._fruit_types_list = [
            {"type": "pineapple", "image": "pineapple.png"},
            {"type": "apple", "image": "apple.png"},
            {"type": "banana", "image": "banana.png"}
        ]
        self._add_image_to_label(self._player_icon, "pineapple_basket.png")
        self._current_player_type_id = 0

        self._game_frame = self.__ui.GameFrame
        self._current_player_position_x = self._player_icon.x()
        self._player_width = self._player_icon.frameGeometry().width()
        self._current_player_position_y = self._player_icon.y()

        # the geometry of a widget and its children is not initialized before we use the show function.
        # Since we need it for calculating our fruit positions we use the show function, but hide it again afterwards
        self.show()
        self.hide()

        self._start_frame_geometry = self._game_frame.frameGeometry()
        self._current_frame_geometry = self._start_frame_geometry

        self._current_score = 0
        self._lcd_score_screen = self.__ui.ScoreScreen

        # rate on which the accelerator value get translated into pixels
        self._standard_translation_rate = -15
        self._fruit_amount = 5
        self._fruit_height = 50
        self._fruit_width = 50
        self._min_fruit_speed = 1
        self._max_fruit_speed = 3
        self._fruit_list = []
        self._create_new_fruits(self._fruit_amount)
        self._is_game_running = False
        self.show()

    def _add_image_to_label(self, label, image_name):
        image = QPixmap(image_name)
        resized_image = image.scaled(label.geometry().width(
        ), label.geometry().height(), QtCore.Qt.KeepAspectRatio)
        label.setPixmap(resized_image)
        label.setStyleSheet("QLabel{ background-color: transparent;}")

    def _init_ui(self):
        self.connect_button = self.__ui.ConnectButton
        self.port_line_edit = self.__ui.PortLineEdit
        self.port_line_edit.setText(self.chosen_port)
        self.connect_button.clicked.connect(self.connect_dippid)
        self.start_button = self.__ui.StartButton
        self.start_button.clicked.connect(self.start_or_pause_game)
        self.explanation_label = self.__ui.ExplanationLabel

    def connect_dippid(self):
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

        self.set_sensor_update_rate_per_s(self.sensor_update_rate_per_s)
        self.dippid.register_callback(
            'button_1', self.decrement_current_player_type)
        self.dippid.register_callback(
            'button_3', self.increment_current_player_type)

    def increment_current_player_type(self, data):
        if int(data) != 0:
            if self._current_player_type_id+1 < len(self._player_types_list):
                self._current_player_type_id += 1
            else:
                self._current_player_type_id = 0
            self._add_image_to_label(
                self._player_icon, self._player_types_list[self._current_player_type_id]["image"])

    def decrement_current_player_type(self, data):
        if int(data) != 0:
            if self._current_player_type_id-1 >= 0:
                self._current_player_type_id -= 1
            else:
                self._current_player_type_id = len(self._player_types_list)-1
            self._add_image_to_label(
                self._player_icon, self._player_types_list[self._current_player_type_id]["image"])

    def start_or_pause_game(self):
        if not self._is_game_running:
            self.set_graphics_update_rate_per_s(
                self.graphics_update_rate_per_s)
            self.start_button.setText("Pause")
            self.explanation_label.setHidden(True)
            self._is_game_running = True
        else:
            self.graphics_update_timer.stop()
            self.start_button.setText("Resume")
            self.explanation_label.setHidden(False)
            self._is_game_running = False

    def _create_new_fruits(self, amount):
        for i in range(amount):
            new_fruit = QLabel("fruit", self._game_frame)
            fruit_x = random.randint(
                0, self._current_frame_geometry.width()-self._fruit_width)
            fruit_y = random.randint(-15, 0)*2
            fruit_id = random.randint(0, len(self._fruit_types_list)-1)
            new_fruit.setGeometry(
                fruit_x, fruit_y-self._fruit_height, self._fruit_width, self._fruit_height)
            self._add_image_to_label(
                new_fruit, self._fruit_types_list[fruit_id]["image"])
            new_fruit_speed = random.randint(
                self._min_fruit_speed, self._max_fruit_speed)
            self._fruit_list.append((new_fruit, new_fruit_speed, fruit_id))

    def update_sensor_data(self):
        if self.dippid is None or not self.dippid.has_capability('accelerometer'):
            return
        v = self.dippid.get_value('accelerometer')
        self._acc_val_x = v['x']

    def set_sensor_update_rate_per_s(self, rate):

        if self.dippid is None:
            return
        if rate == 0:
            self.sensor_update_timer.stop()
        else:
            self.sensor_update_timer.start(int(1000 / rate))

    def set_graphics_update_rate_per_s(self, rate):

        if self.dippid is None:
            return

        if rate == 0:
            self.graphics_update_timer.stop()
        else:
            self.graphics_update_timer.start(int(1000 / rate))

    def update_game(self):
        self.move_player(self._acc_val_x)
        self.move_fruits()
        self.update()

    def update_score(self, score):
        self._current_score += score
        self._lcd_score_screen.display(self._current_score)

    def move_player(self, acc_x_value):
        x_move_value = self._standard_translation_rate*acc_x_value

        # Don't let the player icon x coordinate get bigger than the frame end
        if self._current_player_position_x + self._player_width + x_move_value > self._current_frame_geometry.width():
            self._current_player_position_x = self._current_frame_geometry.width() - \
                self._player_width
        # Don't let the player icon x coordinate get smaller than 0
        elif self._current_player_position_x + x_move_value < 0:
            self._current_player_position_x = 0
        else:
            self._current_player_position_x += x_move_value

        self._player_icon.move(int(self._current_player_position_x), int(
            self._current_player_position_y))

    def move_fruits(self):
        for fruit, speed, fruit_id in self._fruit_list:
            fruit.move(fruit.x(), fruit.y()+speed)
            if fruit.y() > self._current_frame_geometry.height():
                fruit_x = random.randint(
                    0, self._current_frame_geometry.width()-self._fruit_width)
                fruit_y = random.randint(-15, 0)
                fruit.setGeometry(fruit_x, fruit_y-self._fruit_height,
                                  self._fruit_width, self._fruit_height)
            if fruit.geometry().intersects(self._player_icon.geometry()):
                fruit_x = random.randint(
                    0, self._current_frame_geometry.width()-self._fruit_width)
                fruit_y = random.randint(-15, 0)
                fruit.setGeometry(fruit_x, fruit_y-self._fruit_height,
                                  self._fruit_width, self._fruit_height)
                if fruit_id == self._current_player_type_id:
                    self.update_score(10)
                else:
                    self.update_score(-10)

    def resizeEvent(self, event):
        self._current_frame_geometry = self._game_frame.frameGeometry()
        self._current_player_position_y = self._current_frame_geometry.height() - \
            self._player_icon.frameGeometry().height()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        port_arg = sys.argv[1]
        dippidGame = DippidGame(port_arg)
    else:
        dippidGame = DippidGame()

    sys.exit(app.exec_())
