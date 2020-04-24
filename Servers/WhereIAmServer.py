import json
import requests
import cherrypy
import time
import socket


class WhereIAmServer(object):
	def __init__(self):
		file_content=json.load(open('../confFile.json'))
		file_content2=json.load(open('confFileWhereIAm.json'))
		self.port=int(file_content2.get('port'))
		self.catalogPort=int(file_content.get('catalogPort'))
		#self.catalogAddress=file_content2.get('ipCatalog')
		#self.catalogPort=int(file_content2.get('catalogPort'))
		self.catalogAddress=file_content.get('ipCatalog')
		self.DBAddress=""
		self.DBPort=""
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]
		#print(self.address)
	
class WhereIAmRest(object):
	exposed=True	
	def __init__(self):
		
		self.whereIAmServer=WhereIAmServer()
	def GET(self,*uri,**params):
		rdb=json.dumps({"value":False})
		if len(params.values())!=1:
			raise cherrypy.HTTPError(400, "ERROR: missing parameters")
		if list(params.keys())[0]!="chatId":
			raise cherrypy.HTTPError(400, "ERROR: missing parameters")			
		#richiedo il mac con la chatId dal catalog
		try:
			r=requests.get('http://'+str(self.whereIAmServer.catalogAddress)+':'+str(self.whereIAmServer.catalogPort)+'/macRequest?chatToSearch='+str(params["chatId"]))
			if list(r.json().keys())[0]!='mac':
				raise cherrypy.HTTPError(400, "ERROR with parameters")			
			elif r.json()['mac']!=False:
				mac=r.json()['mac'][0][0]
				try:
					rdb1=requests.get('http://'+str(self.whereIAmServer.DBAddress)+':'+str(self.whereIAmServer.DBPort)+'/whereIAm?macToSearch='+str(mac))
					print(rdb1.json()["value"])
					rdb=json.dumps({"value":rdb1.json()["value"]})
				except Exception as e:
					try:
						print("Status code: "+str(rdb1.status_code))
						print("Reason: "+str(rdb1.reason))
					except Exception as e1:
						print(e1)
					print(e)
			else:
				print("MAC NOT FOUND")
		except Exception as e:
			try:
				print("Status code: "+str(r.status_code))
				print("Reason: "+str(r.reason))
			except:
				pass
			print(e)
		return rdb

if __name__=="__main__":
	#inizializzazione 
	whereIAmServerRest=WhereIAmRest()
	conf={
		'/':{
		'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
		}
	}
	port=whereIAmServerRest.whereIAmServer.port
	cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': port})
	cherrypy.tree.mount(whereIAmServerRest,'/',conf)
	cherrypy.engine.start()
	countException=0
	while True and countException<3:
		try:
			catalogAddress=whereIAmServerRest.whereIAmServer.catalogAddress
			catalogPort=whereIAmServerRest.whereIAmServer.catalogPort
			ip=whereIAmServerRest.whereIAmServer.address
			port=whereIAmServerRest.whereIAmServer.port
			body={'whatPut':1,'IP':ip,'port':port, 'last_update':0, 'whoIAm':'WhereIAmServer', 'category':'server','field':''}
			r=requests.put('http://'+str(catalogAddress)+':'+str(catalogPort),json=body)
			timeSleep=r.json()['timeToSleep']
			if r.json()['ipDbServer']!=False and r.json()['port']!=False:
				whereIAmServerRest.whereIAmServer.DBAddress=r.json()['ipDbServer']
				whereIAmServerRest.whereIAmServer.DBPort=r.json()['port']				
				try:
					rdb=requests.get('http://'+str(whereIAmServerRest.whereIAmServer.DBAddress)+':'+str(whereIAmServerRest.whereIAmServer.DBPort))
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
