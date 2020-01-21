from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import fcntl
import os
import sys
import time
import socket
import struct
import io
import zmq
import time
import queue

# The RobotStatusWorker is a thread that updates the cars passed label of the robot with the
# current number of cars that have travelled passed the robot.  It also gets the emergency
# vehicle approaching flag from the robot.
class RobotStatusWorker(QThread):
	sig = pyqtSignal(str, str,str)

	def __init__(self, context, address, port, robot_name, parent=None):
		super(QThread, self).__init__()
		self.robot_name = robot_name
		self.subscriber = context.socket(zmq.SUB)
		self.subscriber.bind("tcp://" + str(address) + ":" + str(port))
		self.subscriber.setsockopt(zmq.SUBSCRIBE, self.robot_name.encode('utf-8')) #subscribes to a specific robot
	
	def run(self):
		print(self.robot_name + ' Car Counting Thread Started')
		try:
			self.running = True
			while self.running:
				[robot_publisher,car_count, emergency_flag] = self.subscriber.recv_multipart()
				car_count = car_count.decode('utf-8')
				emergency_flag = emergency_flag.decode('utf-8')
				
				#print("Recieved %s cars from Robot %s" % robot_publisher,str(car_count))
				self.sig.emit(str(self.robot_name), str(car_count), str(emergency_flag))		
				time.sleep(.25)
		finally:
			print(self.robot_name + 'Car Thread done')

