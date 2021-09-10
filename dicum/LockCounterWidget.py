import logging
import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QLabel

from ConfigManager import ConfigManager


class LockCounterWidget(QWidget):
    def __init__(self, total_locked=ConfigManager().LOCK_LIMIT, total_unlocked=ConfigManager().UNLOCK_LIMIT, current_locked=0, current_unlocked=0):
        super(QWidget, self).__init__()
        self.setLayout(QHBoxLayout(self))
        self.setGeometry(0, 0, 64 * 4, 64)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        self.locked = [QLabel(self) for i in range(total_locked)]
        self.unlocked = [QLabel(self) for i in range(total_unlocked)]

        self.current_locked = len(self.locked) - 1
        self.current_unlocked = current_unlocked

        self.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))
        for i, label in enumerate(self.locked):
            self.layout().addWidget(self.locked[i])
        for i, label in enumerate(self.unlocked):
            self.layout().addWidget(self.unlocked[i])

        self.reset()

        for _ in range(current_locked):
            self.add_locked()
        for _ in range(current_unlocked):
            self.add_unlocked()

        self.layout().addItem(QSpacerItem(10, 1, QSizePolicy.Expanding, QSizePolicy.Preferred))

    def reset(self):
        logging.debug("Lock Counter Widget Resetting.")
        self.current_locked = len(self.locked) - 1
        self.current_unlocked = 0

        for i, _ in enumerate(self.locked):
            self.locked[i].setPixmap(
                QtGui.QPixmap(os.path.join(ConfigManager().ICONS, "lock_icon_closed_gray_64.png")))
            self.locked[i].setGeometry(0, 0, 64, 64)
        for i, _ in enumerate(self.unlocked):
            self.unlocked[i].setPixmap(
                QtGui.QPixmap(os.path.join(ConfigManager().ICONS, "lock_icon_open_gray_64.png")))
            self.unlocked[i].setGeometry(0, 0, 64, 64)

    def add_locked(self):
        try:
            self.locked[self.current_locked].setPixmap(
                QtGui.QPixmap(os.path.join(ConfigManager().ICONS, "lock_icon_closed_64.png")))
        except IndexError:
            logging.critical("exceeding locked images range. there is a bug somewhere...")
            return
        self.current_locked -= 1

    def add_unlocked(self):
        try:
            self.unlocked[self.current_unlocked].setPixmap(
                QtGui.QPixmap(os.path.join(ConfigManager().ICONS, "lock_icon_open_64.png")))
        except IndexError:
            logging.critical("exceeding unlocked images range. there is a bug somewhere...")
            return
        self.current_unlocked += 1

    def set_locked(self):
        for i, label in enumerate(self.locked):
            self.locked[i].setPixmap(
                QtGui.QPixmap(os.path.join(ConfigManager().ICONS, "lock_icon_closed_64.png")))
            self.locked[i].setGeometry(0, 0, 64, 64)
