from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import robotcommands
import zmq
import queue
import time

# Sends commands to the robot
class RobotCommandWorker(QThread):
	sig = pyqtSignal(str)
	
	def __init__(self, context, address, port, robot_name, parent=None):
		super(QThread, self).__init__()
		self.command_queue = queue.Queue()
		self.robot_name = robot_name
		self.command_socket = context.socket(zmq.REP)
		self.command_socket.bind("tcp://" + str(address) + ':' + str(port))
		print(self.robot_name + " RobotCommandWorker started")
		
	# when the robot needs to perform a command. add that command to the queue
	def add_command(self, command):
		print("RobotCommandWorker " + self.robot_name + " added command: " + command)
		self.command_queue.put(command)
		print(self.command_queue.qsize())
				
	def run(self):
		print(self.robot_name + ' RobotCommandWorker started')
		try:
			self.command_socket.recv().decode('utf-8') 
			self.running = True
			print(self.robot_name + " Moving to Stop Position")
			#self.add_command(robotcommands.CMD_ROBOT_RESET_COUNT)
			self.add_command(robotcommands.CMD_ROBOT_STOP)
			while self.running:
				if self.command_queue.qsize() > 0:
					command = self.command_queue.get()
					print("RobotCommandWorker " + self.robot_name + " command sent: " + command)
					self.command_socket.send_string(command)
					message = self.command_socket.recv().decode('utf-8')
					print("RobotCommandWorker " + self.robot_name + " message received: " + message)
				
				time.sleep(0.1)
					
		finally:
			print(self.robot_name + 'RobotCommandWorker done')
