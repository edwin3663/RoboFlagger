import io
import socket
import struct
import time
import picamera
from threading import Thread, Lock
import zmq
import sys
import configparser
import robotcommands
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import pigpio

class RobotFlagger:
	STOP_HAND = 1					# channel controlling stop sign	
	SERVO_MIN = 150				# minimum setting for servo
	SERVO_MAX = 600				# maximum setting for servo
	VIDEO_WIDTH = 640			# video frame width in pixels
	VIDEO_HEIGHT = 480		# video frame height in pixels
	READY = 'R'						# sent after robot establishes a connection
	TIMEOUT = 0.1					# connection timeout

	def __init__(self, config_file):
		# Read the configuration file
		rc = RobotConfig(config_file)
		self.server_address = rc.get_option_str(rc.SERVER_ADDRESS_CFG)
		self.status_port = rc.get_option_str(rc.STATUS_PORT_CFG)
		self.video_port = int(rc.get_option_str(rc.VIDEO_PORT_CFG))
		self.command_port = rc.get_option_str(rc.COMMAND_PORT_CFG)
		self.robot_name = rc.get_option_str(rc.ROBOT_NAME_CFG)
		self.network_adapter = rc.get_option_str(rc.NETWORK_ADAPTER_CFG)
		self.ip_location_port = rc.get_option_str(rc.IP_LOCATION_PORT_CFG)
		self.address_top = rc.get_option_str(rc.ADDRESS_TOP_CFG)
		# Attempt to connect to controller
		connect_to_controller()
		# Initialize PWM controller
		self.pwm = Adafruit_PCA9685.PCA9685()
		self.pwm.set_pwm_freq(50)
	 	# Initialize ZMQ
	 	self.context = zmq.Context()
	 	# Start threads
	 	start_video_thread()
	 	start_processing_thread()

	def attempt_connection(ip, port):
		socket_obj = socket.socket()
		socket_obj.settimeout(TIMEOUT)
		result = socket_obj.connect_ex((ip,int(port)))
		socket_obj.close()
		if (result == 0):
			return True
		else:
			return False

	def connect_to_controller():
		address_bot = 0
		print("Searching for Robot Controller")
		while success == False:
			address = self.address_top + str(address_bot)
			print("Attempting to connect to " + address + " : " + self.ip_location_port)
			success = attempt_connection(address, self.ip_location_port)

			if (address_bot < 255):
				address_bot += 1
			else:
				address_bot = 0
				connection_attempts += 1

			if (connection_attemps >= 4):
				print("Unable to connect to the robot controller")
				print("Aborting")
				sys.exit()
		self.controller_ip = address

	def start_video_thread():
		# Socket for sending video frames to controller
		video_socket = socket.socket()
		video_socket.connect((str(self.controller_ip), self.video_port))
		print("Established pipe for video stream")
		video_thread = Thread(target = send_video, kwargs=dict())
		video_thread.start()
		print("Started video streaming")

	# Thread for sending video over IP
	def send_video():
		connection = None
		try:
			camera = picamera.PiCamera()
			camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
			# let the camera warm up for 2 seconds
			time.sleep(2)
			# Make a file-like object out of the connection
			connection = socket.makefile('wb')
			stream = io.BytesIO()
			for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
				# Write the length of the capture to the stream and flush to
				# ensure it actually gets sent
				connection.write(struct.pack('<L', stream.tell()))
				connection.flush()
				# Rewind the stream and send the image data over the wire
				stream.seek(0)
				connection.write(stream.read())
				# Reset the stream for the next capture
				stream.seek(0)
				stream.truncate()
			
			# Write a length of zero to the stream to signal we're done
			connection.write(struct.pack('<L', 0))
		except socket.error as ex:
			print(ex)
		finally:
			connection.close()
			socket.close()

	def start_process_thread():
		command_socket = self.context.socket(zmq.REQ)
		command_socket.connect("tcp://" + str(self.controller_ip) + ":" + self.command_port)
		print(self.robot_name + " : Established pipe for receiving commands")
		command_thread = Thread(target = process_command, kwargs=dict())
		command_thread.start()
		print(self.robot_name + " : Started command processing thread")
		

	# Receives commands from the controller and tells the robot to perform each action.  
	# When each action is completed it sends a message back to the controller describing the result of the action.
	def process_command(socket, pwm_enabled, i2c_enabled, signboard_enabled, bus):
		try:
			print("Waiting for robot ready")
			socket.send(READY.encode('utf-8'))
			print("Robot Ready")
			running = True
			while running:
				command = socket.recv().decode('utf-8')
				print("Command is: " + str(command))
				if command == robotcommands.CMD_ROBOT_STOP:
					print("set RoboFlagger to 'Stop' configuration")
					set_stop()
					socket.send_string("RoboFlagger in 'Stop' configuration")				
				elif command == robotcommands.CMD_ROBOT_SLOW:
					print("set RoboFlagger to 'Slow' Configuration")
					set_slow()
					socket.send_string("RoboFlagger in 'Slow' configuration")
				else:
					print("command not supported")
					socket.send_string("Command not supported")
			
		except KeyboardInterrupt:
			print("process command interrupted")
		try:
			socket.close()
			sys.exit(0)
		except SystemExit:
			os._exit(0)
			
	def set_stop():
		# pwm.set_pwm(0, 0, 400)
		self.pwm.set_pwm(STOP_HAND, SERVO_MAX)
		
	def set_slow():
		# arm_down(400, servo_min)
		self.pwm.set_pwm(STOP_HAND, SERVO_MIN)
		
if __name__ == "__main__":
	rf = RobotFlagger("../robot_config1/config.txt")
