# -*- coding: iso-8859-15 -*-

import cherrypy
import requests
import json
import time
import socket
import random
import mysql.connector
import re
from datetime import datetime 
import sub.functionsCatalog as fc

class Catalog(object):
	def __init__(self):
		self.actualTime=datetime.now()
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		file_content=json.load(open('../confFile.json'))
		self.port=int(file_content.get("catalogPort"))
		file_content2=json.load(open('confFileCatalog.json'))
		self.user=file_content2.get('dbCatalogUser')
		self.updatingTime=int(file_content2.get('updatingTime'))
		self.randomDelay=int(file_content2.get('randomDelay'))
		self.passwd=file_content2.get('dbCatalogPassword')
		self.myIpAdress=s.getsockname()[0]

	def addDevice(self,mycursor, conn, json_body, timestamp, port):
		fc.addDevice(mycursor, conn, json_body, timestamp, port)
	
	def updateDevice(self,mycursor, conn, json_body, timestamp):
		fc.updateDevice(mycursor, conn, json_body, timestamp)

	def removeInactive(self):
		self.actualTime=datetime.now()
		fc.removeInactive(self.user,self.passwd, self.actualTime,self.updatingTime)

	def removeTelegramBot(self):
		fc.removeTelegramBot(self.user,self.passwd)
		fc.freeEstimotes(self.user,self.passwd)
	
	def foundDbServer(self):
		result1,result2=fc.infoOnDevice(self.user,self.passwd,"DatabaseServer")
		return result1, result2

	def updateOrNewInsert(self, json_body):
		result=fc.updateOrNewInsert(self.user,self.passwd, json_body)
		return result

	def foundTelegramBot(self):
		result0, result1,result2=fc.foundTelegramBot(self.user,self.passwd)
		return result0, result1, result2

	def checkValidityPut(self, json_body):
		result=fc.checkValidityPut(json_body)
		return result

class CatalogREST(object):
	exposed=True	
	def __init__(self,clientID):
		self.ID=clientID
		self.catalog=Catalog()

	#GET METHOD (USED BOTH FOR RETURNING AVAIBLE ESTIMOTE AND MAC ADDRESS FROM CHAT_ID)	
	def GET(self, *uri, **params):
		answer=json.dumps({"value":False}) #DEFAULT ANSWER IF SOMETHING GOES WRONG (BAD REQUEST)
		if len(uri)==1 and uri[0]=='macRequest':
			if len(list(params.keys()))==1 and list(params.keys())[0]=="chatToSearch":
				result=fc.searchForMacAdress(self.catalog.user, self.catalog.passwd, params["chatToSearch"])
				if result==False:
					print("Didn't find that chatId")
				output={'mac':result}
				answer=json.dumps(output)
			else:
				raise cherrypy.HTTPError(400, "ERROR: error with the parameters")

		elif len(uri)==0:
			#list of avaiable estimote
			output=fc.selectAvaiableEstimotes(self.catalog.user, self.catalog.passwd)
			if output==False:
				output=[]
			answer=json.dumps({"values":output})

		else:
			raise cherrypy.HTTPError(400, "ERROR: error with the uri")
		return answer

	def PUT(self):
		body=cherrypy.request.body.read()
		try:
			json_body=json.loads(body.decode('utf-8'))
		except:
			raise cherrypy.HTTPError(400, "ERROR: empty body")
		#print("\nENTERED HERE 1\n")
		#FLAG = 1 --> INSERIMENTO A DATABASE NUOVA OCCORRENZA SERVER / AGGIORNAMENTO
		if json_body['whatPut']==1:
			#print("\nENTERED HERE 2\n")
			port=self.catalog.checkValidityPut(json_body)
			#print("ENTERED HERE 3")
			conn=mysql.connector.connect(host="localhost", user=self.catalog.user, passwd=self.catalog.passwd)
			mycursor=conn.cursor()
			sqlForm="USE credentials_Database"
			try:
				#print("ENTERED HERE 4")
				mycursor.execute(sqlForm)
				timestamp = datetime.now()#.strftime('%Y-%m-%d %H:%M:%S')
				json_body['last_update']=timestamp
				#print(json_body)
				result=self.catalog.updateOrNewInsert(json_body)
				if result==0:	
					self.catalog.addDevice(mycursor, conn, json_body, timestamp, port)
				else:
					oldIp=result[0]
					oldPort=result[1]
					if oldIp==json_body["IP"] and int(oldPort)==int(json_body["port"]):
						#print("AGGIORNATO")
						self.catalog.updateDevice(mycursor, conn, json_body, timestamp)
					else: 
						print("IMPOSSIBLE! "+str(json_body["whoIAm"]))
			except mysql.connector.Error as err:
				print("Something went wrong: {}".format(err))
			timeToSleep=self.catalog.updatingTime+self.catalog.randomDelay*random.uniform(0,1)
			if json_body['category']=="server":
				Ip,port=self.catalog.foundDbServer()
				answer=json.dumps({"timeToSleep":timeToSleep,"ipDbServer":Ip, "port":port})	
			elif json_body['category']=="publisher":
				ipBroker,portBroker=fc.infoOnDevice(self.catalog.user, self.catalog.passwd,"Broker")
				if json_body['field']=='bluetooth':
					toReturn=[]
					toSense=fc.selectUnavaiableMacEstimotes(self.catalog.user, self.catalog.passwd)
					if toSense:
						for element in toSense:
							toReturn.append(element[0])
					elif toSense==False:
						toReturn=[]
					#print(toReturn)
					answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker,"toSense":toReturn})
				else:
					answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker})
			elif json_body['category']=="broker":
				answer=json.dumps({"timeToSleep":timeToSleep})
			else:
				ipBroker,portBroker=fc.infoOnDevice(self.catalog.user, self.catalog.passwd,"Broker")
				answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker})
			return answer

		elif json_body['whatPut']==2:
			result=fc.checkValidityEstimote(self.catalog.user, self.catalog.passwd,json_body['whatPut'],json_body['choice'],json_body['chat_id'])
			print(result)
			if result==True:
				fc.occupyChosenEstimote(self.catalog.user, self.catalog.passwd, json_body['choice'], json_body['chat_id'])

		elif json_body['whatPut']==3:
			result=fc.checkValidityEstimote(self.catalog.user, self.catalog.passwd,json_body['whatPut'],"",json_body['chat_id'])
			if result==True:
				fc.freeChosenEstimote(self.catalog.user, self.catalog.passwd, json_body['chat_id'])
		else:
			raise cherrypy.HTTPError(400, "ERROR: error with params")
		

if __name__ == '__main__':
	catalogClient=CatalogREST('Catalog')
	conf={
		'/':{
		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
		}
	}
	cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': catalogClient.catalog.port})
	cherrypy.tree.mount(catalogClient,'/',conf)
	cherrypy.engine.start()

	countException=0
	while True:
		result=catalogClient.catalog.removeInactive()
		telegramBot=catalogClient.catalog.foundTelegramBot()
		#print(telegramBot)
		if telegramBot[0]==True:
			try:
				user=catalogClient.catalog.user
				pwd=catalogClient.catalog.passwd
				ipWhereIAm,portWhereIAm=fc.infoOnDevice(user,pwd,"WhereIAmServer")
				ipGeneratePath,portGeneratePath=fc.infoOnDevice(user,pwd,"GeneratePathServer")
				strParams="ipWhereIAm="+str(ipWhereIAm)+"&portWhereIAm="+str(portWhereIAm)+"&ipGeneratePath="+str(ipGeneratePath)+"&portGeneratePath="+str(portGeneratePath)
				r=requests.get('http://'+str(telegramBot[1])+':'+str(telegramBot[2])+"?"+str(strParams))
				#print("Going to sleep")
			except requests.exceptions.RequestException as e:
				countException+=1
				print(e)
		if countException==1:
			catalogClient.catalog.removeTelegramBot()
			countException=0
		
		time.sleep(2)
	cherrypy.engine.exit()
