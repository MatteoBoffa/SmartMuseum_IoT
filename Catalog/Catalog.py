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
		#Getting IP dynamically
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.myIpAdress=s.getsockname()[0]
		#Configuration from stati json
		file_content2=json.load(open('confFileCatalog.json'))
		self.port=int(file_content2.get("catalogPort"))
		self.user=file_content2.get('dbCatalogUser')
		self.updatingTime=int(file_content2.get('updatingTime'))
		self.randomDelay=int(file_content2.get('randomDelay'))
		self.passwd=file_content2.get('dbCatalogPassword')

	#FUNCTIONS TO INTERACT WITH SQL DATABASE
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
		#DEFAULT ANSWER IF SOMETHING GOES WRONG (BAD REQUEST)
		answer=json.dumps({"value":False}) 
		#Mac address from chat_id
		if len(uri)==1 and uri[0]=='macRequest':
			if len(list(params.keys()))==1 and list(params.keys())[0]=="chatToSearch":
				result=fc.searchForMacAdress(self.catalog.user, self.catalog.passwd, params["chatToSearch"])
				if result==False:
					print("Didn't find that chatId")
				output={'mac':result}
				answer=json.dumps(output)
			else:
				raise cherrypy.HTTPError(400, "ERROR: error with the parameters")
		#List of avaiable estimotes
		elif len(uri)==0:
			#list of avaiable estimote
			output=fc.selectAvaiableEstimotes(self.catalog.user, self.catalog.passwd)
			if output==False:
				output=[]
			answer=json.dumps({"values":output})
		#Bad request
		else:
			raise cherrypy.HTTPError(400, "ERROR: error with the uri")
		return answer

	#PUT METHOD (USED TO INSERT NEW ELEMENTS IN THE SYSTEM / OCCUPY-FREE ESTIMOTS)
	def PUT(self):
		body=cherrypy.request.body.read()
		try:
			json_body=json.loads(body.decode('utf-8'))
		except:
			raise cherrypy.HTTPError(400, "ERROR: empty body")
		if "whatPut" in list(json_body.keys()) and "category" in list(json_body.keys()):
			#Insert or update of a server into the database
			if json_body['whatPut']==1:
				port=self.catalog.checkValidityPut(json_body)
				conn=mysql.connector.connect(host="localhost", user=self.catalog.user, passwd=self.catalog.passwd)
				mycursor=conn.cursor()
				sqlForm="USE credentials_Database"
				try:
					mycursor.execute(sqlForm)
					timestamp = datetime.now()
					json_body['last_update']=timestamp
					#Check if that server was already present in the database
					result=self.catalog.updateOrNewInsert(json_body)
					if result==0:	
						#If not --> Adding it
						self.catalog.addDevice(mycursor, conn, json_body, timestamp, port)
					else:
						#If it was, updating it if and only if the port and the ip haven't changed 
						#This is done in order to avoid malicius inserts 
						#(if these have actually changed, the server wil run into time out and the next request will add the device with corrected info)
						oldIp=result[0]
						oldPort=result[1]
						if oldIp==json_body["IP"] and int(oldPort)==int(json_body["port"]):
							self.catalog.updateDevice(mycursor, conn, json_body, timestamp)
						else: 
							print("Not possible since that entity is already running on another port/ip! "+str(json_body["whoIAm"]))
				except mysql.connector.Error as err:
					print("The connection for the 'update/insert' failed: {}".format(err))
				#Amount of time after which the server is supposed to contact back the catalog (randomly shifted to help scalability)
				timeToSleep=self.catalog.updatingTime+self.catalog.randomDelay*random.uniform(0,1)
				#Depending on which was the contacting element, we'll provide a different answer
				if json_body['category']=="server":
					#These servers need the presence of the DBserver (if present, its params will appear in the answer)
					Ip,port=self.catalog.foundDbServer()
					answer=json.dumps({"timeToSleep":timeToSleep,"ipDbServer":Ip, "port":port})	
				elif json_body['category']=="publisher":
					#The publishers on the other hand need the catalog's info
					ipBroker,portBroker=fc.infoOnDevice(self.catalog.user, self.catalog.passwd,"BrokerServer")
					if "field" in list(json_body.keys()):
						if json_body['field']=='bluetooth':
							#The simulated estimotes need the list of already taken estimotes (in order to produce consistent data)
							toReturn=[]
							toSense=fc.selectUnavaiableMacEstimotes(self.catalog.user, self.catalog.passwd)
							if toSense:
								for element in toSense:
									toReturn.append(element[0])
							elif toSense==False:
								toReturn=[]
							answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker,"toSense":toReturn})
						else:
							answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker})
					else:
						raise cherrypy.HTTPError(400, "ERROR: error with params")
				elif json_body['category']=="broker":
					answer=json.dumps({"timeToSleep":timeToSleep})
				else:
					ipBroker,portBroker=fc.infoOnDevice(self.catalog.user, self.catalog.passwd,"BrokerServer")
					answer=json.dumps({"timeToSleep":timeToSleep,"ipBroker":ipBroker,"portBroker":portBroker})
				return answer

			elif json_body['whatPut']==2:
				#Option to occupy an estimote
				result=fc.checkValidityEstimote(self.catalog.user, self.catalog.passwd,json_body['whatPut'],json_body['choice'],json_body['chat_id'])
				if result==True:
					fc.occupyChosenEstimote(self.catalog.user, self.catalog.passwd, json_body['choice'], json_body['chat_id'])
			elif json_body['whatPut']==3:
				#Option to free an occupied estimote
				result=fc.checkValidityEstimote(self.catalog.user, self.catalog.passwd,json_body['whatPut'],"",json_body['chat_id'])
				if result==True:
					fc.freeChosenEstimote(self.catalog.user, self.catalog.passwd, json_body['chat_id'])
			else:
				raise cherrypy.HTTPError(400, "ERROR: error with params")
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
	#Counter to check whether the Telegram bot is still active or not
	countException=0
	while True:
		#Catalog will check for timed out server at every iteration
		result=catalogClient.catalog.removeInactive()
		telegramBot=catalogClient.catalog.foundTelegramBot()
		#The only action the catalog has to do is providing the info about the servers if the Telegram bot is active
		if telegramBot[0]==True:
			try:
				user=catalogClient.catalog.user
				pwd=catalogClient.catalog.passwd
				ipWhereIAm,portWhereIAm=fc.infoOnDevice(user,pwd,"WhereIAmServer")
				ipGeneratePath,portGeneratePath=fc.infoOnDevice(user,pwd,"GeneratePathServer")
				strParams="ipWhereIAm="+str(ipWhereIAm)+"&portWhereIAm="+str(portWhereIAm)+"&ipGeneratePath="+str(ipGeneratePath)+"&portGeneratePath="+str(portGeneratePath)
				r=requests.get('http://'+str(telegramBot[1])+':'+str(telegramBot[2])+"?"+str(strParams))
			except requests.exceptions.RequestException as e:
				countException+=1
				print(e)
		if countException==1:
			catalogClient.catalog.removeTelegramBot()
			countException=0
		time.sleep(2)
	cherrypy.engine.exit()
