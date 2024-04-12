import sp

import socket

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),"lib"))

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
		self.BufferSize = 1024
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


	def afterInit(self):
		self.data = self.moduleContainer.addDataParameter("Data")
		self.ip = self.moduleContainer.addIPParameter("Target IP", False)
		self.port = self.moduleContainer.addIntParameter("Port", 10055 , 1, 65535)
		self.log = self.moduleContainer.addBoolParameter("Log", True)
		self.online = self.moduleContainer.addBoolParameter("Online", False)

		#checkStatusAction = self.addAction("Check Status", "checkStatus", self.checkFunction)

		setParameterSetAction = self.addAction("Set Parameter Set", "setParameterSet", self.setParameterSet)
		setParameterSetAction.addIntParameter("Parameter Set", 1, 1, 255)

		getParameterSetAction = self.addAction("Get Parameter Set", "getParameterSet", self.getParameterSet)
		getParameterSetAction.addScriptTokens(["ParameterSet"])

		setGroupVolumeMasterLevelAction = self.addAction("Set Group Volume Master Level", "setGroupVolumeMasterLevel", self.setGroupVolumeMasterLevel)
		setGroupVolumeMasterLevelAction.addIntParameter("Group", 1, 1, 64)
		setGroupVolumeMasterLevelAction.addIntParameter("Level", 0, 0, 144)

		getGroupVolumeMasterLevelAction = self.addAction("Get Group Volume Master Level", "getGroupVolumeMasterLevel", self.getGroupVolumeMasterLevel)
		getGroupVolumeMasterLevelAction.addIntParameter("Group", 1, 1, 64)
		getGroupVolumeMasterLevelAction.addScriptTokens(["Level"])

		setGroupVolumeMasterMuteAction = self.addAction("Set Group Volume Master Mute", "setGroupVolumeMasterMute", self.setGroupVolumeMasterMute)
		setGroupVolumeMasterMuteAction.addIntParameter("Group", 1, 1, 64)
		setGroupVolumeMasterMuteAction.addBoolParameter("Mute", False)

		getGroupVolumeMasterMuteAction = self.addAction("Get Group Volume Master Mute", "getGroupVolumeMasterMute", self.getGroupVolumeMasterMute)
		getGroupVolumeMasterMuteAction.addIntParameter("Group", 1, 1, 64)
		getGroupVolumeMasterMuteAction.addScriptTokens(["Mute"])

		setSlotChannelVolumeAction = self.addAction("Set Slot Channel Volume", "setSlotChannelVolume", self.setSlotChannelVolume)
		setSlotChannelVolumeAction.addEnumParameter("Slot", 0, "1;2;3;4;5;6;7;8;9;A;B")
		setSlotChannelVolumeAction.addIntParameter("Channel", 1, 1, 8)
		setSlotChannelVolumeAction.addIntParameter("Level", 0, 0, 144)

		getSlotChannelVolumeAction = self.addAction("Get Slot Channel Volume", "getSlotChannelVolume", self.getSlotChannelVolume)
		getSlotChannelVolumeAction.addEnumParameter("Slot", 0, "1;2;3;4;5;6;7;8;9;A;B")
		getSlotChannelVolumeAction.addIntParameter("Channel", 1, 1, 8)
		getSlotChannelVolumeAction.addScriptTokens(["Level"])

		setSlotChannelMuteAction = self.addAction("Set Slot Channel Mute", "setSlotChannelMute", self.setSlotChannelMute)
		setSlotChannelMuteAction.addEnumParameter("Slot", 0, "1;2;3;4;5;6;7;8;9;A;B")
		setSlotChannelMuteAction.addIntParameter("Channel", 1, 1, 8)
		setSlotChannelMuteAction.addBoolParameter("Mute", False)

		getSlotChannelMuteAction = self.addAction("Get Slot Channel Mute", "getSlotChannelMute", self.getSlotChannelMute)
		getSlotChannelMuteAction.addEnumParameter("Slot", 0, "1;2;3;4;5;6;7;8;9;A;B")
		getSlotChannelMuteAction.addIntParameter("Channel", 1, 1, 8)
		getSlotChannelMuteAction.addScriptTokens(["Mute"])

		#getSignalLevelAction = self.addAction("Get Signal Level", "getSignalLevel", self.getSignalLevel)
		#getSignalLevelAction.addIntParameter("Slot", 1, 1, 9)
		

		self.addTimer("Checker", 30, self.checkFunction)
		if self.ip.value != "":
			self.checkFunction()
	
	def onParameterFeedback(self, parameter):
		if parameter == self.ip or parameter == self.port:
			self.checkFunction()

	def checkFunction(self):
		if self.log.value == True:
			print("Bose ControlSpace Checker")
		if self.connectTcpSocket():
			self.sendTcpMessage("IP\r")
			recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
			recvData = ""
			if recvMsg[:2] == "IP":
				recvData = recvMsg[3:-1]
			if self.log.value == True:
				print(f"Received msg: {recvMsg}")
			if self.ip.value == recvData:
				if self.log.value == True:
					print("Bose ControlSpace Online")
				self.online.value = True
			else:
				if self.log.value == True:
					print("Bose ControlSpace Offline")
				self.online.value = False
		self.tcpSocket.close()

	def setParameterSet(self, callback, parameterSet):
		self.sendTcpMessage(f"SS {parameterSet}\r")
		callback(True)

	def getParameterSet(self, callback):
		self.sendTcpMessage("GS\r")
		recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
		recvData = ""
		if recvMsg[:1] == "S":
			recvData = recvMsg.split()[1]
		if self.log.value == True:
			print(f"Received msg: {recvMsg}")
		callback(True)
		return {"ParameterSet":recvData}

	def setGroupVolumeMasterLevel(self, callback, group, level):
		self.sendTcpMessage(f"SG {group},{int(level)}\r")
		callback(True)

	def getGroupVolumeMasterLevel(self, callback, group):
		self.sendTcpMessage(f"GG {group}\r")
		recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
		if self.log.value == True:
			print(f"Received msg: {recvMsg}")
		recvData = ""
		if recvMsg[:2] == "GG":
			recvSet = recvMsg.split()[1]
			recvGroup = recvSet.split(",")[0]
			recvData = recvMsg.split(",")[1]
			if int(recvGroup) == group:
				callback(True)
				return {"Level":int(recvData)}
			else:
				if self.log.value == True:
					print("Received msg does not match requested command")
		callback(True)

	def setGroupVolumeMasterMute(self, callback, group, mute):
		self.sendTcpMessage(f"SN {group},{'M' if mute==True else 'U'}\r")
		callback(True)

	def getGroupVolumeMasterMute(self, callback, group):
		self.sendTcpMessage(f"GN {group}\r")
		recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
		if self.log.value == True:
			print(f"Received msg: {recvMsg}")
		recvData = ""
		if recvMsg[:2] == "GN":
			recvSet = recvMsg.split()[1]
			recvGroup = recvSet.split(",")[0]
			recvData = recvMsg.split(",")[1]
			if int(recvGroup) == group:
				callback(True)
				return {"Mute":True if recvData=='M' else False}
			else:
				if self.log.value == True:
					print("Received msg does not match requested command")
		callback(True)
	

	def setSlotChannelVolume(self, callback, slot, channel, level):
		slotstring = ["1", "2", "3", "4", "5", "6","7","8","9","a","b"]
		self.sendTcpMessage(f"SV {slotstring[slot]},{channel},{int(level)}\r")
		callback(True)

	def getSlotChannelVolume(self, callback, slot, channel):
		slotstring = ["1", "2", "3", "4", "5", "6","7","8","9","a","b"]
		self.sendTcpMessage(f"GV {slotstring[slot]},{channel}\r")
		recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
		if self.log.value == True:
			print(f"Received msg: {recvMsg}")
		recvData = ""
		if recvMsg[:2] == "GV":
			recvSet = recvMsg.split()[1]
			recvSlot = recvSet.split(",")[0]
			recvChannel = recvSet.split(",")[1]
			recvData = recvMsg.split(",")[2]
			if recvSlot == slotstring[slot] and int(recvChannel) == channel:
				callback(True)
				return {"Level":int(recvData)}
			else:
				if self.log.value == True:
					print("Received msg does not match requested command")
		callback(True)

	def setSlotChannelMute(self, callback, slot, channel, mute):
		slotstring = ["1", "2", "3", "4", "5", "6","7","8","9","a","b"]
		self.sendTcpMessage(f"SM {slotstring[slot]},{channel},{'M' if mute==True else 'U'}\r")
		callback(True)
	
	def getSlotChannelMute(self, callback, slot, channel):
		slotstring = ["1", "2", "3", "4", "5", "6","7","8","9","a","b"]
		self.sendTcpMessage(f"GM {slotstring[slot]},{channel}\r")
		recvMsg = self.tcpSocket.recv(self.BufferSize).decode()
		if self.log.value == True:
			print(f"Received msg: {recvMsg}")
		recvData = ""
		if recvMsg[:2] == "GM":
			recvSet = recvMsg.split()[1]
			recvSlot = recvSet.split(",")[0]
			recvChannel = recvSet.split(",")[1]
			recvData = recvMsg.split(",")[2]
			if recvSlot == slotstring[slot] and int(recvChannel) == channel:
				callback(True)
				return {"Mute":True if recvData=='M' else False}
			else:
				if self.log.value == True:
					print("Received msg does not match requested command")
		callback(True)
	


if __name__ == "__main__":
	sp.registerPlugin(BoseControlSpace)