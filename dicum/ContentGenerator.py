import csv
import random
import os
import logging

from shutil import copy2
from distutils.dir_util import copy_tree

from jinja2 import Environment, FileSystemLoader

from ConfigManager import ConfigManager
from ConfigManager import ConfigManager
from DequeManager import DequeManager


class ContentGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(ConfigManager().TEMPLATES))
        self.available_images = []
        self.__index_image_folder()
        #self.commands = self.__get_commands()

        try:
            copy_tree(ConfigManager().SCRIPTS, os.path.join(ConfigManager().TEMP_LOCATION, "js"))
            copy_tree(ConfigManager().STYLES, os.path.join(ConfigManager().TEMP_LOCATION, "styles"))
            copy2(os.path.join(ConfigManager().IMAGES, ConfigManager().BG_IMAGE), ConfigManager().TEMP_IMAGES + "/")
        except FileNotFoundError:
            logging.critical("Content could not be loaded. file not found error")
            exit(1)

    def get_next(self):
        try:
            return self.commands.pop()
        except IndexError:
            logging.error("get_next failed, no more elements to pop")
            return None

    def get_restricted(self, end_time_iso):
        template = self.env.get_template("restricted.html")
        return template.render(restricted_time=end_time_iso,
                               background_image=os.path.join(ConfigManager().TEMP_IMAGES, ConfigManager().BG_IMAGE))

    def get_unrestricted(self):
        template = self.env.get_template("unrestricted.html")
        return template.render(background_image=os.path.join(ConfigManager().TEMP_IMAGES, ConfigManager().BG_IMAGE))

    def get_current_restriction(self, restriction_time, text=""):
        time_string = str(restriction_time).split(":")[0] + " hours"
        template = self.env.get_template("restriction_time.html")
        return template.render(current_restriction_time=time_string,
                               background_image=os.path.join(ConfigManager().TEMP_IMAGES, ConfigManager().BG_IMAGE),
                               text=text)

    def get_task_view(self):
        template = self.env.get_template("task_dialog.html")
        return template.render()

    @staticmethod
    def __is_image(filename):
        supported_types = [".jpeg", ".jpg", ".png", ".webp"]
        for type in supported_types:
            if filename.lower().endswith(type):
                return True
        return False

    def __index_image_folder(self):
        self.available_images = os.listdir(ConfigManager().IMAGES)
        self.available_images.remove(ConfigManager().BG_IMAGE)
        self.available_images = [image for image in self.available_images if self.__is_image(image)]
        random.shuffle(self.available_images)

    def __interpret_command(self, command):

        kind, content, time = command
        if kind == "task":
            template = self.env.get_template("task_dialog.html")
            return "html", template.render(), time

        elif kind == "img":
            template = self.env.get_template("plain_image.html")
            img_file_name = content.strip()
            if img_file_name == "":
                try:
                    logging.info("Using random Image")
                    img_file_name = self.available_images.pop()
                except IndexError:
                    logging.error("Usage of random Image failed. No more images available!")
                    img_file_name = ConfigManager().BG_IMAGE
            if not os.path.isfile(os.path.join(ConfigManager().TEMP_IMAGES, img_file_name)):
                try:
                    copy2(os.path.join(ConfigManager().IMAGES, img_file_name), ConfigManager().TEMP_IMAGES + "/")
                except FileNotFoundError:
                    logging.error("Image file could not be found:", img_file_name)
            return "html", template.render(image_filename="images/" + img_file_name), time
        else:
            return command
    """
    def __get_commands(self):
        commands = []
        with open(ConfigManager().COMMANDS) as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            for row in reader:
                commands.append(self.__interpret_command(row))

        random.shuffle(commands)
        return commands
    """

# TODO 5 min viewing time for web page
# TODO Chose 3 of 5 Cards with Pictures (Cens/NoCens)
