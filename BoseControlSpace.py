import sp

import socket

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"lib"))

# Still need to check when connection sometimes drops out.

class BoseControlSpace(sp.BaseModule):

	#plugin info used 
	pluginInfo = {
		"name" : "Bose ControlSpace",
		"description" : "SP Plugin for communicating with Bose devices via ControlSpace Serial Control Protocol v5.8",
		"author" : "SP",
		"version" : (1, 0),
		"spVersion" : (1, 2, 0),
		"helpPath" : os.path.join(os.path.dirname(os.path.abspath(__file__)),"help.md")
	}

	def __init__(self):
		sp.BaseModule.__init__(self)
		self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.BufferSize = 1024

	def connectTcpSocket(self):
		self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.ip.value != "":
			try:
				if self.log.value == True:
					print(f"Bose ControlSpace connecting to: {self.ip.value}:{int(self.port.value)}")
				self.tcpSocket.connect((self.ip.value, int(self.port.value)))
				if self.log.value == True:
					print(f"Bose ControlSpace connected")
					self.online.value = True
				return True
			except socket.error as e: 
				if self.log.value == True:
					print ("Connection error: %s" % e) 
				self.online.value = False
				return False
		else:
			if self.log.value == True:
				print("Bose ControlSpace Host IP not defined")
			self.online.value = False
			return False
		
	def sendTcpMessage(self, msg):
		if self.connectTcpSocket():
			if self.log.value == True:
				print(f"Bose ControlSpace Sent Message: {msg}")
			sent = self.tcpSocket.send(msg.encode())
			if sent == 0:
				if self.log.value == True:
					print("Bose ControlSpace Socket Connection Broken")
			recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
			self.tcpSocket.close()
			return recvMsg

	def checkFunction(self):
		if self.connectTcpSocket():
			recvMsg = self.sendTcpMessage("IP\r\n")
			recvData = ""
			if recvMsg[:2] == "IP":
				recvData = recvMsg[3:-1]
			print(f"Received msg: {recvMsg}")
			print(f"Returned IP: {recvData}")
			if self.ip.value == recvData:
				if self.log.value == True:
					print("Bose ControlSpace Online")
				self.online.value = True
			else:
				if self.log.value == True:
					print("Bose ControlSpace Offline")
				self.online.value = False
		self.tcpSocket.close()

	def afterInit(self):
		self.data = self.moduleContainer.addDataParameter("Data")
		self.ip = self.moduleContainer.addIPParameter("Target IP", False)
		self.port = self.moduleContainer.addIntParameter("Port", 10055 , 1, 65535)
		self.log = self.moduleContainer.addBoolParameter("Log", True)
		self.online = self.moduleContainer.addBoolParameter("Online", False)

		checkStatusAction = self.addAction("Check Status", "checkStatus", self.checkFunction)

		setParameterSetAction = self.addAction("Set Parameter Set", "setParameterSet", self.setParameterSet)
		setParameterSetAction.addIntParameter("Parameter Set", 1, 1, 255)  

		setGroupVolumeMasterLevelAction = self.addAction("Set Group Volume Master Level", "setGroupVolumeMasterLevel", self.setGroupVolumeMasterLevel)
		setGroupVolumeMasterLevelAction.addIntParameter("Group", 1, 1, 64)
		setGroupVolumeMasterLevelAction.addIntParameter("Level", 0, 0, 144)

		setGroupVolumeMasterMuteAction = self.addAction("Set Group Volume Master Mute", "setGroupVolumeMasterMute", self.setGroupVolumeMasterMute)
		setGroupVolumeMasterMuteAction.addIntParameter("Group", 1, 1, 64)
		setGroupVolumeMasterMuteAction.addBoolParameter("Mute", False)

		self.addTimer("Checker", 30, self.checkFunction)
		if self.log.value == True:
			print("Bose ControlSpace Checker")
		if self.ip.value != "":
			self.checkFunction()
	
	def onParameterFeedback(self, parameter):
		if parameter == self.ip or parameter == self.port:
			self.checkFunction()

	def setParameterSet(self, parameterSet):
		self.sendTcpMessage(f"SS {parameterSet}\r\n")

	def setGroupVolumeMasterLevel(self, group, level):
		self.sendTcpMessage(f"SG {group},{level}\r\n")

	def setGroupVolumeMasterMute(self, group, mute):
		self.sendTcpMessage(f"SN {group},{'M' if mute==True else 'U'}\r\n")

if __name__ == "__main__":
	sp.registerPlugin(BoseControlSpace)