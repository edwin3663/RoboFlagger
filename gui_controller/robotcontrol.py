from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import robotcommands

VIDEO_WIDTH		= 320
VIDEO_HEIGHT	= 240

# RobotControl is a widget that controls a single robot		
class RobotControl(QWidget):

	def __init__(self, robot_name, robot_status_worker, robot_command_worker, video_reader ):
		QWidget.__init__(self)
		self.robot_name = robot_name
		self.sign_slow = False
		self.robot_status_worker = robot_status_worker
		self.robot_command_worker = robot_command_worker
		self.video_reader = video_reader

		# load graphics for labels
		self.stop_pic = QPixmap('Stop.png')
		self.stop_pic = self.stop_pic.scaled(50,50,Qt.KeepAspectRatioByExpanding, Qt.FastTransformation) 
		self.slow_pic = QPixmap('Slow.jpg')
		self.slow_pic = self.slow_pic.scaled(50,50,Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
		self.create_widget()

	def create_widget(self):
		# main layout widget
		layout = QVBoxLayout(self)
		
		# robot sign position
		status_layout = QHBoxLayout()
		status_layout.addWidget(QLabel(self.robot_name))
		self.sign_pos_label = QLabel('')
		self.sign_pos_label.setPixmap(self.stop_pic)
		status_layout.addWidget(self.sign_pos_label)
		self.robot_status_worker.start()
		self.robot_status_worker.sig.connect(self.on_update_status)
		layout.addLayout(status_layout)

		# video feed
		self.video_label = QLabel(self.robot_name + ' video feed unavailable')
		self.video_label.setMinimumSize(VIDEO_WIDTH, VIDEO_HEIGHT)
		self.video_label.setMaximumSize(VIDEO_WIDTH, VIDEO_HEIGHT)
		self.video_reader.start()
		self.video_reader.sig.connect(self.on_updated_frame)
		layout.addWidget(self.video_label)

		# slow/stop button
		self.slow_stop_button = QPushButton('Set ' + self.robot_name + ' to slow')
		self.slow_stop_button.setStyleSheet("color: orange")
		self.slow_stop_button.clicked.connect(self.switch_sign)
		self.robot_command_worker.start()
		layout.addWidget(self.slow_stop_button)

	#TODO: Remove
	def on_update_status(self, robot_name, car_count, emergency_flag):
		self.carCount = car_count
		self.emergencyFlag = emergency_flag

	def on_updated_frame(self):
		self.video_label.setPixmap(QPixmap(self.video_reader.image_loc))

	# tells the robot to switch its sign from slow or stop
	def switch_sign(self):
		print(self.robot_name + " change sign")
		if (self.sign_slow == True):
			print ("Controller sent STOP signal")
			self.robot_command_worker.add_command(robotcommands.CMD_ROBOT_STOP)
			self.slow_stop_button.setText("Set " + self.robot_name + " to slow")
			self.slow_stop_button.setStyleSheet("color: orange")
			self.sign_pos_label.setPixmap(self.stop_pic)
			self.sign_slow = False
		else:
			print ("Controller sent SLOW signal")
			self.robot_command_worker.add_command(robotcommands.CMD_ROBOT_SLOW)
			self.slow_stop_button.setText("Set " + self.robot_name + " to stop")
			self.slow_stop_button.setStyleSheet("color: red")
			self.sign_pos_label.setPixmap(self.slow_pic)
			self.sign_slow = True

	def ReturnRobotName(self):
		return self.robot_name
