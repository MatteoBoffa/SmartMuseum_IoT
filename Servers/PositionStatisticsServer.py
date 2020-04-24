import json
import requests
import cherrypy
import time
import socket
import datetime
import threading
import sub.PositionThread as pt

class PositionStatisticServer(object):
	def __init__(self):
		file_content=json.load(open('../confFile.json'))
		self.catalogAddress=file_content.get('ipCatalog')
		self.catalogPort=int(file_content.get('catalogPort'))
		file_content2=json.load(open('confFilePositionStat.json'))
		#self.catalogAddress=file_content2.get('ipCatalog')
		#self.catalogPort=int(file_content2.get('catalogPort'))
		self.DBAddress=""
		self.DBPort=""
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

	def update_freeboard(self):
		DBAdress=self.DBAddress
		DBPort=self.DBPort
		#print("\nUpdating SmartMuseum_Gen...")
		a=pt.GetWithThread("all",1,"SmartMuseum_rooms_tot_rep","SmartMuseum_rooms_tot_nr",DBAdress,DBPort)
		a.start()
		#print("Updating SmartMuseum_Cur...")
		b=pt.GetWithThread("today",0,"SmartMuseum_rooms_day_rep","SmartMuseum_rooms_day_nr",DBAdress,DBPort)
		b.start()
		return a.ident,b.ident

if __name__=="__main__":
	#inizializzazione 
	positionStatisticServer=PositionStatisticServer()
	countException=0
	threadId1=0
	threadId2=0
	while True and countException<3:
		try:
			body={'whatPut':1,'IP':positionStatisticServer.address,'port':False, 'last_update':0, 'whoIAm':'PosStatServer', 'category':'server','field':''}
			r=requests.put('http://'+str(positionStatisticServer.catalogAddress)+':'+str(positionStatisticServer.catalogPort),json=body)
			timeSleep=r.json()['timeToSleep']
			if r.json()['ipDbServer']!=False and r.json()['port']!=False:
				positionStatisticServer.DBAddress=r.json()['ipDbServer']
				positionStatisticServer.DBPort=r.json()['port']				
				try:
					counter=0
					for item in threading.enumerate():
						if item.ident==threadId1 or item.ident==threadId2:
							counter+=1
					if counter==0:
						threadId1,threadId2=positionStatisticServer.update_freeboard()
				except requests.exceptions.RequestException as e:
					print(e)
			else:
				print('\tDB not connected yet')
			#print("Going to sleep for "+str(timeSleep))
		except requests.exceptions.RequestException as e:
			countException+=1
			print(e)
			timeSleep=2

		time.sleep(timeSleep)
