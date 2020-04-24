import json
import requests
import cherrypy
import time
import socket
import datetime
import operator
from copy import deepcopy

#GLOBAL VARIABLES
finalPath=0
maxScore=0

class GeneratePathServer(object):
	def __init__(self):
		file_content=json.load(open('../confFile.json'))
		self.catalogAddress=file_content.get('ipCatalog')
		self.catalogPort=int(file_content.get('catalogPort'))
		file_content2=json.load(open('confFileGeneratePath.json'))
		self.port=int(file_content2.get('port'))
		#self.catalogAddress=file_content2.get('ipCatalog')
		#self.catalogPort=int(file_content2.get('catalogPort'))
		self.DBAddress=""
		self.DBPort=""
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

	def enterRecursion(self,roomsToVisit,timeLeft, actualRoom, sorted_d, points):
		#print(actualRoom)
		global finalPath
		global maxScore

		if points>maxScore:
			finalPath=deepcopy(roomsToVisit)
			maxScore=points
			"""
			print("FOUND")
			print("WITH THE FOLLOWING SCORE:")
			print(maxScore)
			print("WITH FOLLOWING PATH")
			print(roomsToVisit)
			"""
		for key in sorted_d.keys():
			#print("The key is "+str(key)+" while the value is "+ str(actualRoom))
			if str(key)!=str(actualRoom):
				
				if key not in roomsToVisit:
					#REMEMBER: DECIDED 10 MINUTES PER ROOM!
					#ABS(ORIGIN_ROOM-DESTINATION_ROOM) MINUTES TO MOVE FROM A ROOM TO THE OTHER
					difference=timeLeft-abs(int(key)-int(actualRoom))-10

					if difference>=0:
						points=points+int(sorted_d[key])
						timeLeft=difference
						roomsToVisit.append(key)
						self.enterRecursion(roomsToVisit,timeLeft, key, sorted_d, points)
						timeLeft=timeLeft+abs(int(key)-int(actualRoom))+10
						points=points-int(sorted_d[key])
						roomsToVisit.pop(len(roomsToVisit)-1)

class GeneratePathRest(object):
	exposed=True	
	def __init__(self):
		self.generatePathServer=GeneratePathServer()

	def GET(self,*uri,**params):

		global finalPath
		global maxScore
		toReturn=json.dumps({"value":False})
		if len(params)!=1:
			#print("STOPPED HERE!")
			raise cherrypy.HTTPError(400, "ERROR: bad request")	
		else:
			try:
				#AT THIS POINT CHECK THAT DURATION > MINIMUM TO SEE A ROOM (IF IT'S NOT, SUGGEST TO COME BACK!)
				timeInMinutes=int(params["duration"])
				if timeInMinutes<10:
					print("ATTENTION: NOT EVEN TIME TO SEE A ROOM")
				else:
					try:
						rdb=requests.get('http://'+str(self.generatePathServer.DBAddress)+':'+str(self.generatePathServer.DBPort)+'/positions?typeOfRequest=all')
						if rdb.json()["value"]!=False and rdb.json()["value"]!=[]:
							listOfPositions=rdb.json()["value"]
							dictionaryPositionMac={}
							dictionarySecondUse={}
							rooms={}
						
							for item in listOfPositions:
								#IF-ELSE IN WHICH I GET THE SCORES FOR EACH ROOM
								if str(item[1])+" "+item[2] not in dictionaryPositionMac:
									#NOTE: dictionarySecondUse.keys() WILL CONTAIN THE ROOMS IN WHICH I HAVE MEASURES
									if str(item[1]) not in dictionarySecondUse:
										dictionarySecondUse[str(item[1])]=1
									else:
										dictionarySecondUse[str(item[1])]+=1
									dictionaryPositionMac[str(item[1])+" "+item[2]]=item[3]
								else:
									lastDate=datetime.datetime.strptime(dictionaryPositionMac[str(item[1])+" "+item[2]],'%Y-%m-%d %H:%M:%S')
									date=datetime.datetime.strptime(item[3],'%Y-%m-%d %H:%M:%S')
									difference=date-lastDate
									seconds=difference.days*24*60*60+difference.seconds
									if seconds>=20:
										dictionarySecondUse[str(item[1])]=dictionarySecondUse[str(item[1])]+1
							sorted_d = dict(sorted(dictionarySecondUse.items(), key=operator.itemgetter(1),reverse=True))
							
							finalPath=[]
							roomsToVisit=[]
							#SUPPOSE WE NEED 10 MINUTES PER ROOM
							timeLeft=timeInMinutes-10
							actualRoom=int(list(sorted_d.keys())[0])
							finalPath.append(list(sorted_d.keys())[0])
							roomsToVisit.append(list(sorted_d.keys())[0])
							maxScore=int(sorted_d[list(sorted_d.keys())[0]])
							points=int(sorted_d[list(sorted_d.keys())[0]])
							self.generatePathServer.enterRecursion(roomsToVisit,timeLeft, actualRoom, sorted_d, points)
							result={'roomsScores':sorted_d, 'maxScore': maxScore, 'finalPath':finalPath}
							toReturn=json.dumps({'value':result})
						elif rdb.json()["value"]==[]:
							toReturn=json.dumps({'value':[]})
					except Exception as e:
						print("Status code: "+str(rdb.status_code))
						print(e)
			except:
				#print("STOPPED HERE ON THE OTHER HAND")
				raise cherrypy.HTTPError(400, "ERROR: bad request")			
		return toReturn

if __name__=="__main__":
	#inizializzazione 
	generatePathServerRest=GeneratePathRest()
	conf={
		'/':{
		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
		}
	}
	port=generatePathServerRest.generatePathServer.port
	cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': port})
	cherrypy.tree.mount(generatePathServerRest,'/',conf)
	cherrypy.engine.start()
	countException=0
	while True and countException<3:
		try:
			catalogAddress=generatePathServerRest.generatePathServer.catalogAddress
			catalogPort=generatePathServerRest.generatePathServer.catalogPort
			ip=generatePathServerRest.generatePathServer.address
			port=generatePathServerRest.generatePathServer.port
			body={'whatPut':1,'IP':ip,'port':port, 'last_update':0, 'whoIAm':'GeneratePathServer', 'category':'server','field':''}
			r=requests.put('http://'+str(catalogAddress)+':'+str(catalogPort),json=body)
			timeSleep=r.json()['timeToSleep']
			if r.json()['ipDbServer']!=False and r.json()['port']!=False:
				generatePathServerRest.generatePathServer.DBAddress=r.json()['ipDbServer']
				generatePathServerRest.generatePathServer.DBPort=r.json()['port']				
				try:
					rdb=requests.get('http://'+str(generatePathServerRest.generatePathServer.DBAddress)+':'+str(generatePathServerRest.generatePathServer.DBPort))
					#print(rdb.text)
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
	cherrypy.engine.exit()
