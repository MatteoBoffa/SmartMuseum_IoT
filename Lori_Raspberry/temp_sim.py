import paho.mqtt.client as PahoMQTT
import time
import datetime
import json
import random
import socket
import requests

class Sensor(object):
	"""sensore simulato"""
	def __init__(self,roomID,tempBool):#,broker):
		

				###CATALOG
		file_content=json.load(open('../confFile.json'))
		self.catalogAddress=file_content.get('ipCatalog')
		self.catalogPort=int(file_content.get('catalogPort'))
		file_content2=json.load(open('confFileTemp.json'))
		#self.catalogAddress=file_content2.get('ipCatalog')
		#self.catalogPort=int(file_content2.get('catalogPort'))	

		self.buildingID=file_content2.get('buildingID')
		self.roomID=roomID
		self.sensorID=file_content2.get('sensorID')
		self.ipMessageBroker=""
		self.portMessageBroker=""
		self.isTemp=tempBool
		self.minTemp=int(file_content2.get('minTemp'))
		self.maxTemp=int(file_content2.get('maxTemp'))
		self.topic='/'.join([str(self.buildingID),str(self.roomID),str(self.sensorID)])
		self._paho_mqtt = PahoMQTT.Client(self.topic, False) 
		self._paho_mqtt.on_connect = self.myOnConnect
		self.message={
			'room':self.roomID,
			#'sensorID':self.sensorID,
			'value': '',
			'timestamp':'',
					
			}	

		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

	def __repr__(self):
		return json.dumps(self.message)

	def start(self,ipBroker,portBroker):
		self.ipMessageBroker=ipBroker
		self.portMessageBroker=portBroker
		self._paho_mqtt.connect(self.ipMessageBroker, self.portMessageBroker)
		self._paho_mqtt.loop_start()
		if self.isTemp==True:
			self.temp=random.randint(self.minTemp,self.maxTemp)
		print(f"Simulated sensor {self.roomID} for temperature started")

	def sendData(self):
		var=int(random.choice([-1,0,0,0,0,1])) #temperature variation
		self.temp=self.temp+var
		self.message['value']=self.temp
		#self.message['value']=random.randint(10,30)
		#self.message['timestamp']=str(datetime.datetime.now())

		local_time = datetime.datetime.now()
		date=local_time.strftime('%d-%m-%Y %H:%M:%S')
		self.message['timestamp']=str(date)

		self.myPublish(self.topic,json.dumps(self.message))
		#print(json.dumps(self.message))

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, message, 2)
		print("Published under topic %s"%topic)
		print(message)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.ipMessageBroker, rc))

	def stop(self):
		self.ipMessageBroker=""
		self.portMessageBroker=""
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def updateBroker(self,ipBroker,portBroker):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()
		self.ipMessageBroker=ipBroker
		self.portMessageBroker=portBroker
		self._paho_mqtt.connect(self.ipMessageBroker, self.portMessageBroker)
		self._paho_mqtt.loop_start()
		print(f"Broker has changed to {self.ipMessageBroker}!")

if __name__ == '__main__':

	#buildingID='SmartMuseum'
	roomID=str(input('Insert the room number for this simulated temperature sensor:\t'))
	while (roomID.isdigit())==False:
		roomID=str(input('Insert the room number for this simulated temperature sensor. MUST BE INTEGER!\t'))	

	sensor=Sensor(roomID,True)

	consec_e=0
	count=1

	while True and consec_e<3:
		if count==13:
			#print("Go back to 1")
			count=1
		try:
			body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'sim_temp_sensor_'+roomID, 'category':'publisher','field':'temp'}
			r=requests.put('http://'+str(sensor.catalogAddress)+':'+str(sensor.catalogPort),json=body)
			time_sleep=r.json()['timeToSleep']
			newIpBroker=r.json()['ipBroker']
			newPortBroker=r.json()['portBroker']
			if newIpBroker!="" and newPortBroker!="" and sensor.ipMessageBroker=="" and sensor.portMessageBroker=="":
				sensor.start(newIpBroker,newPortBroker)
			elif newIpBroker!="" and newPortBroker!="" and newIpBroker!=sensor.ipMessageBroker and newPortBroker!=sensor.portMessageBroker:
				sensor.updateBroker(newIpBroker,newPortBroker)
			elif (newIpBroker=="" or newPortBroker=="") and (newIpBroker!=sensor.ipMessageBroker or newPortBroker!=sensor.portMessageBroker):
				print("LOST BROKER")
				sensor.stop()
			elif sensor.ipMessageBroker=="" and sensor.portMessageBroker=="":
				print("STILL NO BROKER!")
			#print("Sensor updated in catalog!")
			try:
				if count==12 and sensor.ipMessageBroker!="" and sensor.portMessageBroker!="":
					sensor.sendData()
				consec_e=0
			except Exception as e:
				print(e)

		except requests.exceptions.RequestException as e:
			print(e)
			consec_e+=1
			print("Error. Go to sleep for 5 seconds, then retry...")
			time_sleep=5

		finally:
			count=count+1
			time.sleep(time_sleep)

	print("Catalog seems to be down... killing process...")	
	time.sleep(3)	
	exit()

