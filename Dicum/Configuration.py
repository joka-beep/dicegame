import os
import sys
import tempfile
import logging
from datetime import datetime

from shutil import copy2

from DequeManager import *


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller. Copied from
	 https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile """
	if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	else:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


class Configuration:
	class __Configuration:
		def __init__(self, commands_file=None, deque_file=None):
			self.LOCK_LIMIT = 2
			self.UNLOCK_LIMIT = 2

			self.HOME = os.getenv('HOME')
			self.CONFIG = os.path.join(self.HOME, ".config", "dicum")
			if not os.path.isdir(self.CONFIG):
				os.makedirs(self.CONFIG)

			if not commands_file:
				commands_file = "game.csv"
			self.COMMANDS = os.path.join(self.CONFIG, commands_file)
			if not os.path.isfile(self.COMMANDS):
				with open(self.COMMANDS, "w+") as file:
					logging.warning("game.csv could not be found. Creating default!")
					file.write(
						"num,2,0\nnum,3,0\nnum,5,0\nnum,5,0\nnum,12,0\nlock,unlock,0\nlock,unlock,0\nlock,lock,0\nlock,lock,0")

			self.GAME_CONFIG = self.COMMANDS

			if not deque_file:
				deque_file = "deque.yaml"
			self.DEQUE_FILE = os.path.join(self.CONFIG, deque_file)
			if not os.path.isfile(self.DEQUE_FILE):
				logging.warning("Deque configuration not found, creating from default.")
				default_deque = [BlackCard(3), BlackCard(3), BlackCard(3), BlackCard(3), RedCard("Fuck with dildo", 12), RedCard("Cum while in chastity", 12), GreenCard()]
				DequeManager.save_specific_deque(self.DEQUE_FILE, default_deque)


			self.LOCK_TIME_LOCATION = os.path.join(self.CONFIG, "time")
			if not os.path.isfile(self.LOCK_TIME_LOCATION):
				with open(self.LOCK_TIME_LOCATION, "w+") as file:
					file.write(datetime.now().isoformat())

			# Can be changed by the user and during runtime - e.g. Images etc...
			self.RESOURCES = os.path.join(self.CONFIG, "resources")
			if not os.path.isdir(self.RESOURCES):
				os.makedirs(self.RESOURCES)

			self.IMAGES = os.path.join(self.RESOURCES, "images")
			if not os.path.isdir(self.IMAGES):
				os.makedirs(self.IMAGES)
				copy2(os.path.join(Configuration().BASE_RESOURCES, "images", "README"), self.IMAGES + "/")
				copy2(os.path.join(Configuration().BASE_RESOURCES, "images", "bg.png"), self.IMAGES + "/")

			# Cannot be changed by the user, icons, templates etc...
			self.BASE_RESOURCES = resource_path("resources")

			self.TEMPLATES = os.path.join(self.BASE_RESOURCES, "templates")
			if not os.path.isdir(self.TEMPLATES):
				logging.error("Templates not found. Continuing but errors might occur.")

			self.SCRIPTS = os.path.join(self.TEMPLATES, "js")
			if not os.path.isdir(self.SCRIPTS):
				logging.error("Scripts not found. Continuing but errors might occur.")
			self.STYLES = os.path.join(self.TEMPLATES, "styles")
			if not os.path.isdir(self.STYLES):
				logging.error("Styles not found. Continuing but errors might occur.")

			self.ICONS = os.path.join(self.BASE_RESOURCES, "icons")
			if not os.path.isdir(self.ICONS):
				logging.error("Icons not found. Continuing but errors might occur.")

			with tempfile.TemporaryDirectory() as temp_dir:
				self.TEMP_LOCATION = temp_dir
			logging.info('created temporary directory' + temp_dir)

			self.TEMP_IMAGES = os.path.join(self.TEMP_LOCATION, "images")
			self.TEMP_SCRIPTS = os.path.join(self.TEMP_LOCATION, "js")
			self.HTML_REL_PATH = "file://" + self.TEMP_LOCATION + "/"
			self.BG_IMAGE = "bg.png"

			try:
				os.makedirs(self.TEMP_LOCATION)
			except FileExistsError:
				pass
			try:
				os.makedirs(self.TEMP_IMAGES)
			except FileExistsError:
				pass
			try:
				os.makedirs(self.TEMP_SCRIPTS)
			except FileExistsError:
				pass

			if not os.path.isfile(self.LOCK_TIME_LOCATION):
				logging.critical("Dicum time file does not exist.")

		def __str__(self):
			return repr(self)

	instance = None

	def __init__(self):
		if not Configuration.instance:
			Configuration.instance = Configuration.__Configuration()
		else:
			Configuration.instance

	def __getattr__(self, name):
		return getattr(self.instance, name)
