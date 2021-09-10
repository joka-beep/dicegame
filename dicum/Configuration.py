import logging
import os
import sys
import tempfile
import yaml

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
		yaml_tag = "!Configuration.__Configuration"
		def __init__(self):
			self.LOCK_LIMIT = 2
			self.UNLOCK_LIMIT = 2
			self.DEQUE_FILE = os.path.join(self.CONFIG, "deque.yaml")
			self.TIME_FILE = os.path.join(self.CONFIG, "time")
			self.LOCK_STATUS_FILE = os.path.join(self.CONFIG, "lock_status")
			self.RESOURCES = os.path.join(self.CONFIG, "resources")
			self.BASE_RESOURCES = resource_path("resources")
			self.IMAGES = os.path.join(self.RESOURCES, "images")
			self.TEMPLATES = os.path.join(self.BASE_RESOURCES, "templates")
			self.SCRIPTS = os.path.join(self.TEMPLATES, "js")
			self.STYLES = os.path.join(self.TEMPLATES, "styles")
			self.ICONS = os.path.join(self.BASE_RESOURCES, "icons")

			self.setup_directories()
			self.setup_temp_dir()

		def __str__(self):
			return repr(self)
		
		def __repr__(self):
			return f"{self.__class__.__name__}(" \
				"LOCK_LIMIT={self.LOCK_LIMIT}," \
				"UNLOCK_LIMIT={self.UNLOCK_LIMIT}," \
				"DEQUE_FILE={self.DEQUE_FILE}," \
				"TIME_FILE={self.TIME_FILE}," \
				"LOCK_STATUS_FILE={self.LOCK_STATUS_FILE}," \
				"RESOURCES={self.RESOURCES}," \
				"BASE_RESOURCES={self.BASE_RESOURCES}," \
				"IMAGES={self.IMAGES}," \
				"TEMPLATES={self.TEMPLATES}," \
				"SCRIPTS={self.SCRIPTS}," \
				"STYLES={self.STYLES}," \
				"ICONS={self.ICONS})"

		def setup_temp_dir(self):
			# Setup temporary directory for web pages that are rendered
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

		def setup_directories(self):
			if not os.path.isdir(self.CONFIG):
				os.makedirs(self.CONFIG)
					
			if not os.path.isfile(self.DEQUE_FILE):
				logging.warning("Deque configuration not found, creating from default.")
				default_deque = [BlackCard(3), BlackCard(3), BlackCard(3), BlackCard(3), GreenCard(), GreenCard(), GreenCard(), GreenCard(), GreenCard(), GreenCard()]
				DequeManager.save_specific_deque(self.DEQUE_FILE, default_deque)

			if not os.path.isfile(self.TIME_FILE):
				with open(self.TIME_FILE, "w+") as file:
					file.write(datetime.now().isoformat())
			if not os.path.isfile(self.LOCK_STATUS_FILE):
				with open(self.LOCK_STATUS_FILE, "w") as file:
					file.write("0\n0")
			
			if not os.path.isdir(self.RESOURCES):
				os.makedirs(self.RESOURCES)
			
			if not os.path.isdir(self.IMAGES):
				os.makedirs(self.IMAGES)
				copy2(os.path.join(self.BASE_RESOURCES, "images", "README"), self.IMAGES + "/")
				copy2(os.path.join(self.BASE_RESOURCES, "images", "bg.png"), self.IMAGES + "/")

			if not os.path.isdir(self.TEMPLATES):
				logging.error("Templates not found. Continuing but errors might occur.")
			if not os.path.isdir(self.SCRIPTS):
				logging.error("Scripts not found. Continuing but errors might occur.")
			if not os.path.isdir(self.STYLES):
				logging.error("Styles not found. Continuing but errors might occur.")
			if not os.path.isdir(self.ICONS):
				logging.error("Icons not found. Continuing but errors might occur.")

	@staticmethod
	def save_config():
		file_path = os.path.join(os.getenv('HOME'), ".config", "dicum", "config.yaml")
		with open(file_path, "w") as file:
			file.write(yaml.dump(Configuration.instance))

	@staticmethod
	def load_config():
		file_path = os.path.join(os.getenv('HOME'), ".config", "dicum", "config.yaml")
		with open(file_path, "r") as file:
			text = file.read()
			logging.debug(text)
			Configuration.instance = yaml.load(text, Loader=yaml.Loader)

	
	### Singleton Stuff
	instance = None

	def __init__(self):
		if not Configuration.instance:
			Configuration.load_config()
			#Configuration.instance = Configuration.__Configuration()
		else:
			Configuration.instance

	def __getattr__(self, name):
		return getattr(self.instance, name)
