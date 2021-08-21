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

logging.basicConfig(level=logging.DEBUG)


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
		self.time_restrictor = TimeRestrictor()
		self.timer = QTimer(self)
		self.timer.timeout.connect(lambda: self.stop_restriction())
		self.generator = ContentGenerator()
		self.deque = DequeManager(Configuration().DEQUE_FILE)
		self.view = QtWebEngineWidgets.QWebEngineView()
		
		self.card_widget = QWidget(self)
		self.card_widget.setLayout(QGridLayout())
		self.card_button_array = []
		self.__setup_card_widget()
		
		self.base_widget = QWidget(self)
		self.base_widget.setLayout(QHBoxLayout())
		self.__setup_base_widget()
		
		self.lock_counter = 0
		self.unlock_counter = 0
		self.__load_lock_status()
		self.lock_counter_widget = LockCounterWidget(current_locked=self.lock_counter, current_unlocked=self.unlock_counter)
		#self.lock_counter_widget.setObjectName("lock_counter")
		
		self.__setup_ui()
			
		self.show_welcome_screen()


	def __load_lock_status(self):
		with open(Configuration().LOCK_STATUS_FILE) as file:
			lines = file.readlines()
			print(lines)
			if len(lines) < 2:
				logging.warning("Lock status file malformatted")
			self.lock_counter = int(lines[0].strip())
			self.unlock_counter = int(lines[1].strip())

	def __setup_base_widget(self):
		self.base_widget.setGeometry(0, 0, 0, 130)
		self.base_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		self.base_widget.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Ignored, QSizePolicy.Preferred))
		self.base_widget.layout().addWidget(self.card_widget)
		self.base_widget.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Ignored, QSizePolicy.Preferred))

	def __setup_card_widget(self):
		# self.button_rows = self.isqrt(self.generator.get_size())
		# self.button_cols = self.button_rows if self.button_rows * (self.button_rows + 1) > self.generator.get_size() else self.button_rows + 1
		button_rows = 1
		button_cols = self.deque.get_size()
		for i in reversed(range(self.card_widget.layout().count())): 
			self.card_widget.layout().itemAt(i).widget().setParent(None)
		self.card_button_array = [StyledPushButton() for _ in range(self.deque.get_size())]
		for row in range(button_rows):
			for col in range(button_cols):
				pos = row * button_cols + col
				self.card_widget.layout().addWidget(self.card_button_array[pos], row, col)
				self.card_button_array[pos].clicked.connect(partial(self.draw_card, pos))


	def __run_ui(self):
		self.show_welcome_screen()
		if self.time_restrictor.is_restricted():
			self.lock_counter_widget.set_locked()


	def __reset_ui(self):
		self.__load_lock_status()
		self.__setup_card_widget()
		self.__setup_base_widget()
		self.show_welcome_screen()


	def __setup_ui(self):
		self.setLayout(QVBoxLayout())
		self.layout().addWidget(self.lock_counter_widget)
		self.layout().addWidget(self.view)
		self.layout().addWidget(self.base_widget)

		
	def draw_card(self, pos):
		card = self.deque.get_card()

		# update button
		self.card_button_array[pos].setEnabled(False)
		self.card_button_array[pos].setText(card.kind)
		print(card.kind)

		if card.kind == "green":
			self.unlock_counter += 1
			self.lock_counter_widget.add_unlocked()
			if self.unlock_counter >= Configuration().UNLOCK_LIMIT:
				self.stop_restriction()
			else:
				self.view.setHtml(
				                  self.generator.get_current_restriction(self.time_restrictor.current_restriction_time,
						                                                 text="Lucky you! Maybe I'll release you this time."),
						          QUrl(Configuration().HTML_REL_PATH))
		
		elif card.kind == "black":
			self.lock_counter += 1
			self.lock_counter_widget.add_locked()
			self.time_restrictor.update_restriction_time(card.hours)
			if self.lock_counter >= Configuration().LOCK_LIMIT:
				self.start_restriction()
			else:
				self.view.setHtml(
					self.generator.get_current_restriction(self.time_restrictor.get_current_restriction_time(),
				                                       text="How unfortuneate, you picked a Lock!\nI've added " + str(card.hours) + "h to your Lockup!"),
				QUrl(Configuration().HTML_REL_PATH))

		elif card.kind == "yellow": # todo implement functionality
			logging.error("Not implemented yet.")
			# add cards to deck
			# update the button widget
		elif card.kind == "red":
			self.view.setHtml(self.generator.get_task_view(), QUrl(Configuration().HTML_REL_PATH))
		else:
			logging.error("Card type not handled")


	def show_welcome_screen(self):
		if self.time_restrictor.is_restricted():
			self.show_locked_screen()
		else:
			self.view.setHtml(self.generator.get_unrestricted(), QUrl(Configuration().HTML_REL_PATH))
			self.activate_buttons()
			self.timer.stop()
	
	def show_locked_screen(self):
			self.view.setHtml(self.generator.get_restricted(self.time_restrictor.get_end_time_iso()),
			                  QUrl(Configuration().HTML_REL_PATH))
			self.deactivate_buttons()
			self.timer.setInterval(self.time_restrictor.get_remaining_time().microseconds)
			self.timer.start()

	def start_restriction(self):
		logging.info("Start Restriction")
		self.deactivate_buttons()
		self.lock_counter = 0
		self.unlock_counter = 0
		self.store_lock_status()
		self.time_restrictor.store_restriction_time()
		self.show_locked_screen()

	def stop_restriction(self):
		logging.info("Stop Restriction")
		self.lock_counter_widget.reset()
		self.__setup_card_widget()
		self.unlock_counter = 0
		self.lock_counter = 0
		self.time_restrictor.store_restriction_time(datetime.now())
		self.time_restrictor.reset()
		self.store_lock_status()
		self.show_welcome_screen()

	def activate_buttons(self):
		for button_number in range(self.card_widget.layout().count()):
			try:
				self.card_widget.layout().itemAt(button_number).widget().setEnabled(True)
				self.card_widget.layout().itemAt(button_number).widget().setText("")
			except AttributeError:
				logging.error("Non-button element in button widget, could not be disabled.")

	def deactivate_buttons(self):
		for button_number in range(self.card_widget.layout().count()):
			try:
				self.card_widget.layout().itemAt(button_number).widget().setEnabled(False)
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

	def store_lock_status(self):
		with open(Configuration().LOCK_STATUS_FILE, "w") as file:
			file.write(str(self.lock_counter) + "\n")
			file.write(str(self.unlock_counter) + "\n")


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
		self.main_widget.deque.save_deque()
		self.main_widget.store_lock_status()
		event.accept()


if __name__ == '__main__':
	app = QApplication([])
	app.setStyleSheet(
		"QPushButton { background-color: darkred; color: black } QMainWindow { background-color: black }")
	main_window = MainWindow()

	sys.exit(app.exec())
