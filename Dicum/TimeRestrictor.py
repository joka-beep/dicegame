import os
import logging
from datetime import datetime, timedelta

from Configuration import Configuration


class TimeRestrictor():
	def __init__(self):
		self.BASE_FORMAT = "%H:%M:%S"

		self.current_restriction_time = timedelta(hours=0)
		self.restriction_time_changed = False

		self.config_filepath = Configuration().LOCK_TIME_LOCATION
		self.restriction_endtime = datetime.max
		self.session_start = datetime.now()
		if not os.path.isfile(self.config_filepath):
			with open(self.config_filepath, "w") as file:
				file.write(datetime.now().isoformat())

		with open(self.config_filepath, "r") as file:
			restriction_time = file.readline().strip()

		try:
			self.restriction_endtime = datetime.fromisoformat(restriction_time)
		except ValueError:
			logging.error("Restriction time could not be retrieved from storage.")

	def get_end_time_iso(self):
		return self.restriction_endtime.isoformat()

	def get_remaining_time(self):
		return self.restriction_endtime - datetime.now()

	def is_restricted(self):
		return (self.restriction_endtime - datetime.now()).total_seconds() > 0

	def store_restriction_time(self, timestamp=None):
		if not timestamp:
			timestamp = datetime.now() + self.current_restriction_time
		with open(self.config_filepath, "r+") as file:
			file.seek(0)
			file.write(timestamp.isoformat())

	def update_restriction_time(self, time_string):
		self.restriction_time_changed = True
		delta = self.parse_time(time_string)
		self.current_restriction_time += delta
		return self.current_restriction_time

	@staticmethod
	def parse_time(time_string):
		time_delta = timedelta()
		try:
			time_delta = timedelta(hours=int(time_string))
		except ValueError:
			logging.error("Time string could not be parsed to integer (hours):", time_string)
		return time_delta
