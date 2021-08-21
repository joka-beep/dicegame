#!/bin/python3


import os
import sys
import logging
import tempfile

from functools import partial
from datetime import datetime

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QHBoxLayout, \
	QSpacerItem, QSizePolicy
from PyQt5.QtCore import QTimer, QUrl

from Configuration import Configuration
from ContentGenerator import ContentGenerator
from DequeManager import DequeManager
from TimeRestrictor import TimeRestrictor
from LockCounterWidget import LockCounterWidget


class StyledPushButton(QPushButton):
	def __init__(self, *args, **kwargs):
		super(QPushButton, self).__init__(*args, **kwargs)
		# self.setFixedSize(QSize(100, 50))
		self.setFixedHeight(130)
		self.setFixedWidth(85)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setStyleSheet(
			"QPushButton { font-family: Love Story Rough;} :enabled { color: white; border-image:url(" + os.path.join(
				Configuration().ICONS,
				"pc_red_black.jpg") + "); } :disabled { color: #222222; border-image:url(" + os.path.join(
				Configuration().ICONS, "pc_red_spades.jpg") + "); }")


class MainGameWidget(QWidget):
	def __init__(self):
		super(QWidget, self).__init__()
		self.__reset()
		self.__setup_ui()
		self.__run_ui()

	def __run_ui(self):
		self.update_welcome()
		if self.time_restrictor.is_restricted():
			self.lock_counter_widget.set_locked()

	def __reset(self):
		self.lock_counter = 0
		self.unlock_counter = 0
		self.time_restrictor = TimeRestrictor()
		self.timer = QTimer(self)
		self.timer.timeout.connect(lambda: self.update_welcome())

		lock_counter = self.findChild(LockCounterWidget, "lock_counter")
		if lock_counter:
			lock_counter.reset()
		self.generator = ContentGenerator()
		self.deque = DequeManager(Configuration().DEQUE_FILE)

	def __setup_ui(self):
		# calculate button row and column length based on number of commands
		self.button_array = [StyledPushButton() for _ in range(self.deque.get_size())]

		# self.button_rows = self.isqrt(self.generator.get_size())
		# self.button_cols = self.button_rows if self.button_rows * (self.button_rows + 1) > self.generator.get_size() else self.button_rows + 1
		self.button_rows = 1
		self.button_cols = self.deque.get_size()

		self.button_widget = QWidget(self)
		# self.button_widget.setFixedSize(500, 130)
		# self.button_widget.setFixedHeight(130)
		self.button_widget.setLayout(QGridLayout())
		for row in range(self.button_rows):
			for col in range(self.button_cols):
				pos = row * self.button_cols + col
				self.button_widget.layout().addWidget(self.button_array[pos], row, col)
				self.button_array[pos].clicked.connect(partial(self.get_content, pos))

		self.button_widget.setSizePolicy(
			QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

		# Setting up the view
		self.view = QtWebEngineWidgets.QWebEngineView()

		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QHBoxLayout())
		self.base_widget.setGeometry(0, 0, 0, 130)
		self.base_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		self.base_widget.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Ignored, QSizePolicy.Preferred))
		self.base_widget.layout().addWidget(self.button_widget)
		self.base_widget.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Ignored, QSizePolicy.Preferred))

		self.setLayout(QVBoxLayout())
		self.lock_counter_widget = LockCounterWidget()
		self.lock_counter_widget.setObjectName("lock_counter")
		self.layout().addWidget(self.lock_counter_widget)
		self.layout().addWidget(self.view)
		self.layout().addWidget(self.base_widget)

	def get_content(self, pos):
		drawn_card = self.deque.get_card()
		content_item = self.generator.generate_content_for_card(drawn_card)

		if not content_item:
			return
		kind, content, time = content_item

		# update button
		self.button_array[pos].setEnabled(False)
		self.button_array[pos].setText(kind)

		if kind == "url":
			self.view.load(QtCore.QUrl(content))
		elif kind == "html":
			self.view.setHtml(content, QUrl(Configuration().HTML_REL_PATH))
		elif kind == "num":
			self.view.setHtml(
				self.generator.get_current_restriction(self.time_restrictor.update_restriction_time(content),
				                                       text="I've added " + content + "h to your Lockup!"),
				QUrl(Configuration().HTML_REL_PATH))
		elif kind == "lock":
			if content == "lock":
				self.lock_counter += 1
				self.lock_counter_widget.add_locked()
				if self.lock_counter >= Configuration().LOCK_LIMIT:
					self.start_restriction()
				else:
					self.view.setHtml(
						self.generator.get_current_restriction(self.time_restrictor.current_restriction_time,
						                                       text="How unfortunate, you picked a Lock!"),
						QUrl(Configuration().HTML_REL_PATH))

			elif content == "unlock":
				self.unlock_counter += 1
				self.lock_counter_widget.add_unlocked()
				if self.unlock_counter >= Configuration().UNLOCK_LIMIT:
					self.stop_restriction()
				else:
					self.view.setHtml(
						self.generator.get_current_restriction(self.time_restrictor.current_restriction_time,
						                                       text="Lucky you! Maybe I'll release you this time."),
						QUrl(Configuration().HTML_REL_PATH))
			else:
				logging.info("lock value invalid, ignoring")
		else:
			logging.info("content kind was not recognized:" + kind + content)

	def update_welcome(self, timer=None):
		if self.time_restrictor.is_restricted():
			self.view.setHtml(self.generator.get_restricted(self.time_restrictor.get_end_time_iso()),
			                  QUrl(Configuration().HTML_REL_PATH))
			self.deactivate_buttons()
			self.timer.setInterval(self.time_restrictor.get_remaining_time().microseconds)
			self.timer.start()
		else:
			self.view.setHtml(self.generator.get_unrestricted(), QUrl(Configuration().HTML_REL_PATH))
			self.activate_buttons()
			self.lock_counter_widget.reset()
			if timer:
				timer.stop()

	def start_restriction(self):
		logging.info("Start Restriction")
		self.time_restrictor.store_restriction_time()
		self.__reset()
		self.__run_ui()

	def stop_restriction(self):
		logging.info("Stop Restriction")
		self.time_restrictor.store_restriction_time(datetime.now())
		self.__reset()
		self.__run_ui()

	def activate_buttons(self):
		for button_number in range(self.button_widget.layout().count()):
			try:
				self.button_widget.layout().itemAt(button_number).widget().setEnabled(True)
				self.button_widget.layout().itemAt(button_number).widget().setText("")
			except AttributeError:
				logging.error("Non-button element in button widget, could not be disabled.")

	def deactivate_buttons(self):
		for button_number in range(self.button_widget.layout().count()):
			try:
				self.button_widget.layout().itemAt(button_number).widget().setEnabled(False)
			except AttributeError:
				logging.error("Non-button element in button widget, could not be disabled.")

	@staticmethod
	def isqrt(n):
		x = n
		y = (x + 1) // 2
		while y < x:
			x = y
			y = (x + n // x) // 2
		return x


class MainWindow(QMainWindow):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setWindowTitle("Dicum")
		# self.menuBar().addMenu("Dicum")
		self.main_widget = MainGameWidget()
		self.setCentralWidget(self.main_widget)
		self.setGeometry(0, 0, 1500, 1250)

		self.show()

	def closeEvent(self, event):
		if self.main_widget.time_restrictor.restriction_time_changed:
			self.main_widget.time_restrictor.store_restriction_time()
		self.main_widget.deque.save_deque()
		event.accept()


if __name__ == '__main__':
	#logging.basicConfig(filename=tempfile.TemporaryFile().name, level=logging.DEBUG)
	logging.basicConfig(level=logging.DEBUG)

	app = QApplication([])
	app.setStyleSheet(
		"QPushButton { background-color: darkred; color: black } QMainWindow { background-color: black }")
	main_window = MainWindow()

	sys.exit(app.exec())
