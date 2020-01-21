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

# Thread runs in the background waiting for connection from the robots
class IPLocationWorker(QThread):
	def __init__(self, server_address, ip_find_port):
		super(QThread, self).__init__()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((server_address, int(ip_find_port)))
		self.sock.listen(1)
		
	def run(self):
		print("listening for connection from robots")
		count = 0
		while count < 2:
			connection, client_address = self.sock.accept()
			try:
				print ('connection from', client_address)
				count += 1
			finally:
				print("connection closed")
				connection.close()

		self.sock.close()
		print("socket closed")
