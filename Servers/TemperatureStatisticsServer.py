import json
import requests
import cherrypy
import time
import socket
import sub.TemperatureThread as tt
import threading

class TemperatureStatisticsServer(object):
	def __init__(self):
		file_content2=json.load(open('confFileTemperatureStat.json'))
		self.catalogAddress=file_content2.get('ipCatalog')
		self.catalogPort=int(file_content2.get('catalogPort'))
		self.DBAddress=""
		self.DBPort=""
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

	def update_freeboard(self):
		#The freeboard page is uploaded every n seconds (since the get request takes some time, no requests are send if the past one isn't finished)
		DBAdress=self.DBAddress
		DBPort=self.DBPort
		print("\nUpdating SmartMuseum_Gen...")
		a=tt.GetWithThread("all","SmartMuseum_tot_temp",DBAdress,DBPort)
		a.start()
		print("Updating SmartMuseum_Cur...")
		b=tt.GetWithThread("today","SmartMuseum_day_temp",DBAdress,DBPort)
		b.start()
		return a.ident,b.ident

if __name__=="__main__":
	temperatureStatisticsServer=TemperatureStatisticsServer()
	countException=0
	threadId1=0
	threadId2=0
	while True and countException<3:
		try:
			#Every n seconds has to contact both the catalog and, if possible, the database!
			body={'whatPut':1,'IP':temperatureStatisticsServer.address,'port':False, 'last_update':0, 'whoIAm':'TempStatsServer', 'category':'server','field':''}
			r=requests.put('http://'+str(temperatureStatisticsServer.catalogAddress)+':'+str(temperatureStatisticsServer.catalogPort),json=body)
			timeSleep=r.json()['timeToSleep']
			if r.json()['ipDbServer']!=False and r.json()['port']!=False:
				temperatureStatisticsServer.DBAddress=r.json()['ipDbServer']
				temperatureStatisticsServer.DBPort=r.json()['port']				
				try:
					counter=0
					for item in threading.enumerate():
						if item.ident==threadId1 or item.ident==threadId2:
							counter+=1
					if counter==0:
						threadId1,threadId2=temperatureStatisticsServer.update_freeboard()
				except requests.exceptions.RequestException as e:
					print(e)
			else:
				print('\tDB not connected yet')
			print("Going to sleep for "+str(timeSleep))
		except requests.exceptions.RequestException as e:
			countException+=1
			print(e)
			timeSleep=2

		time.sleep(timeSleep)