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


class ConfigManager():
    class __ConfigManager():
        def __init__(self):
            self.file_path = os.path.join(os.getenv('HOME'), ".config", "dicum", "config.yaml")
            with open(self.file_path, "r") as file:
                text = file.read()
                logging.debug(text)
                self.config = yaml.load(text, Loader=yaml.Loader)
            self.setup_temp_dir()

        def save_config(self):
            with open(self.file_path, "w") as file:
                file.write(yaml.dump(self.config))

        def setup_temp_dir(self):
            # Setup temporary directory for web pages that are rendered
            with tempfile.TemporaryDirectory() as temp_dir:
                self.config["TEMP_LOCATION"] = temp_dir
            logging.info('created temporary directory' + temp_dir)

            self.config["TEMP_IMAGES"] = os.path.join(self.config["TEMP_LOCATION"], "images")
            self.config["TEMP_SCRIPTS"] = os.path.join(self.config["TEMP_LOCATION"], "js")
            self.config["HTML_REL_PATH"] = "file://" + self.config["TEMP_LOCATION"] + "/"
            self.config["BG_IMAGE"] = "bg.png"

            try:
                os.makedirs(self.config["TEMP_LOCATION"])
            except FileExistsError:
                pass
            try:
                os.makedirs(self.config["TEMP_IMAGES"])
            except FileExistsError:
                pass
            try:
                os.makedirs(self.config["TEMP_SCRIPTS"])
            except FileExistsError:
                pass

        # Singleton Stuff
    instance = None

    def __init__(self):
        if not ConfigManager.instance:
            # ConfigManager.load_config()
            ConfigManager.instance = ConfigManager.__ConfigManager()
        else:
            ConfigManager.instance

    def __getattr__(self, name):
        return self.instance.config[name]
        return getattr(self.instance, config)[name]
