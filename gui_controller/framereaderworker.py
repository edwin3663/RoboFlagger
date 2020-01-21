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

# The FrameReaderWorker is a thread that reads video frames from the 
# robot
class FrameReaderWorker(QThread):
	sig = pyqtSignal()

	def __init__(self, address, port, video_frame_file):
		super(QThread, self).__init__()
		self.image_loc = video_frame_file
		self.server_socket = socket.socket()
		self.server_socket.bind((address,port))
		self.server_socket.listen(0)
		
	def run(self):
		connection = self.server_socket.accept()[0].makefile('rb')
		print("Video Thread Started")
		try:
			self.running = True
			while self.running:
				image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
				# if the image length is 0 quit the loop and stop the thread
				if not image_len:
					self.running = False
					break

				# construct a stream to hold the image data and read the image
				image_stream = io.BytesIO()
				image_stream.write(connection.read(image_len))
				image_stream.seek(0)
				
				with open(self.image_loc, 'wb') as out:
					out.write(image_stream.read())

				self.sig.emit() # emit a signal to tell the gui its time to update the label image
		finally:
			connection.close()
			self.server_socket.close()
