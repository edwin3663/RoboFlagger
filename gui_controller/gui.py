from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import zmq
import sys
import robo_library
from robotcontrol import RobotControl
from robotcommandworker import RobotCommandWorker
from robotstatusworker import RobotStatusWorker
from framereaderworker import FrameReaderWorker
from iplocationworker import IPLocationWorker
from threading import Thread

# CONSTANTS
ROBOT1_NAME	= "Robot 1"
ROBOT2_NAME = "Robot 2"
VIDEO_WIDTH		= 320
VIDEO_HEIGHT		= 240
R1_VIDEO_PORT		= 8000
R1_COMMAND_PORT		= 8001
R1_COUNT_PORT		= 8002
R2_VIDEO_PORT		= 8003
R2_COMMAND_PORT		= 8004
R2_COUNT_PORT		= 8005
IP_LOCATION_PORT	= 8007
NET_ADAPTER = 'wlp0s20f3'

# Main application GUI
class MainWindow(QWidget):

	def __init__(self, net_adapter):
		QWidget.__init__(self)
		self.setWindowTitle("RoboFlagger Control")
		server_address = robo_library.get_ip(NET_ADAPTER)
		print("Controller IP Address Found: " + server_address)
		
		context = zmq.Context()

		location_service = IPLocationWorker(server_address, IP_LOCATION_PORT)
		location_service.start()
		
		r1_status_worker = RobotStatusWorker(context, server_address, R1_COUNT_PORT, ROBOT1_NAME)
		r1_command_worker =	RobotCommandWorker(context, server_address, R1_COMMAND_PORT, ROBOT1_NAME)
		r1_video_reader = FrameReaderWorker(server_address, R1_VIDEO_PORT, "r1_video.jpg")
		self.r1 = RobotControl(ROBOT1_NAME, r1_status_worker, r1_command_worker, r1_video_reader)
		
		r2_status_worker = RobotStatusWorker(context, server_address, R2_COUNT_PORT, ROBOT2_NAME)
		r2_command_worker =	RobotCommandWorker(context, server_address, R2_COMMAND_PORT, ROBOT2_NAME)
		r2_video_reader = FrameReaderWorker(server_address, R2_VIDEO_PORT, "r2_video.jpg")	
		self.r2 = RobotControl(ROBOT2_NAME, r2_status_worker, r2_command_worker, r2_video_reader)

		vlayout = QVBoxLayout(self)
		robot_layout = QHBoxLayout()
		robot_layout.addWidget(self.r1)
		robot_layout.addWidget(self.r2)
		vlayout.addLayout(robot_layout)
		self.show()

#Main 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow(NET_ADAPTER)
	sys.exit(app.exec_())
