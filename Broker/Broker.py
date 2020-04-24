import os
import psutil
import time
import json
import socket
import requests

class BrokerServer(object):
	def __init__(self):
		file_content2=json.load(open('confFileBroker.json'))
		self.catalogPort=int(file_content2.get('catalogPort'))
		self.catalogAddress=file_content2.get('ipCatalog')	
		self.portAdress=int(file_content2.get('brokerPort'))	
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

if __name__ == '__main__':
	brokerServer=BrokerServer()
	countException=0
	while True and countException<3:
		# Iterate over all running process
		found=False
		for proc in psutil.process_iter():
			try:
				# Get process name & pid from process object.
				processName = proc.name()
				if processName=="mosquitto":
					found=True
					break
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				pass
		if found==True:
			try:
				body={'whatPut':1,'IP':brokerServer.address,'port':brokerServer.portAdress, 'last_update':0, 'whoIAm':'BrokerServer', 'category':'broker','field':''}
				r=requests.put('http://'+str(brokerServer.catalogAddress)+':'+str(brokerServer.catalogPort),json=body)
				timeSleep=r.json()['timeToSleep']
			except requests.exceptions.RequestException as e:
				countException+=1
				print(e)
				timeSleep=2
		else:
			print("NO ACTIVE MOSQUITTO SERVICE!")
			countException+=1
			timeSleep=2

		time.sleep(timeSleep)

