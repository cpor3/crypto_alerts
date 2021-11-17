import threading
import requests
import time
from datetime import datetime, timezone, timedelta

class Infinite_Thread():
	"""
	Prevents heroku app on going idle
	Needed only with free dyno types
	"""
	def __init__(self, app_ping_uri: str, update_interval_seg=90):
		self.__app_ping_uri = app_ping_uri
		self.counter = 0
		self.active = False
		self.update_interval_seg = update_interval_seg # 90 = 15 minutes
		self.start_time = 0
		self.thread = threading.Thread(target=self.infinite_thread)
		self.thread.setDaemon(True)

	def start(self, start_counter=0):
		self.counter = start_counter
		self.active = True
		self.start_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
		self.thread.start()

	def stop(self):
		self.active = False

	def is_active(self) -> bool:
		return self.active

	def infinite_thread(self) -> None:
		print('Running infinite thread...\n')

		while self.active:
			self.counter += 1

			# send a request every update_interval
			if self.counter > self.update_interval_seg:
				self.counter = 0
				requests.get(self.__app_ping_uri)
				print('Request sent.')

			# give some time to shut down properly when a SIGTERM signal is received (avoid SIGKILL signal)  
			time.sleep(10) 

		print('Infinite thread stopped\n')

