import time
import datetime
import json
import paho.mqtt.client as PahoMQTT
import random
import socket
import requests

#import classes as c

class SimulatedBluetoothScan():
	def __init__(self,roomID,blBool):
		file_content=json.load(open('../confFile.json'))
		self.catalogAddress=file_content.get('ipCatalog')
		self.catalogPort=int(file_content.get('catalogPort'))
		file_content2=json.load(open('confFileBl.json'))
		#self.catalogAddress=file_content2.get('ipCatalog')
		#self.catalogPort=int(file_content2.get('catalogPort'))
		self.buildingID=file_content2.get('buildingID')
		self.roomID=roomID
		self.sensorID=file_content2.get('sensorID')
		self.listOfEstimotes=file_content2.get('estimotes')

		self.ipMessageBroker=""
		self.portMessageBroker=""
		self.isBlue=blBool

		self.topic='/'.join([str(self.buildingID),str(self.roomID),str(self.sensorID)])

		self._paho_mqtt = PahoMQTT.Client(self.topic, False) 
		self._paho_mqtt.on_connect = self.myOnConnect
	
		self.message={
			'room':self.roomID,
			'value': '',
			'timestamp':'',
			}

		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

		self.toSense=[]

	def start(self,ipBroker,portBroker):
		self.ipMessageBroker=ipBroker
		self.portMessageBroker=portBroker
		self._paho_mqtt.connect(self.ipMessageBroker, self.portMessageBroker)
		self._paho_mqtt.loop_start()
		if self.isBlue==True:
			self.bls=[]
		print(f"Sensor {str(self.roomID)} for bluetooth scanning simulation started")

	def sendData(self):
		estimotes={}
		for estimote in self.listOfEstimotes:
			estimotes[estimote]=0
		for it in self.toSense:
			for it2 in estimotes.keys():
				if it==it2:
					estimotes[it2]=1
		for e in estimotes.keys():
			if estimotes[e]==1:
				temp=random.choice([0,0,0,0,1])
				if temp==1:
					self.bls.append(e)				
		#superfluo, tenuto perchè tanto nnìon fa nulla
		tosend=[]
		for bl in self.bls:
			if bl in self.listOfEstimotes:
				tosend.append(bl)
		self.message['value']=tosend #self.bls
		if tosend:
			local_time = datetime.datetime.now()
			date=local_time.strftime('%d-%m-%Y %H:%M:%S')
			self.message['timestamp']=str(date)

			self.myPublish(self.topic,json.dumps(self.message))
			print(json.dumps(self.message))
		self.bls=[]

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, message, 2)
		print("Published under topic %s"%topic)

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

	roomID=str(input('Insert the room number for this simulated Bluetooth scanner:\t')) 
	#cambiare qua per ogni simulazione, magari con sys.argv in fase di lancio
	while (roomID.isdigit())==False:
		roomID=str(input('Insert the room number for this simulated Bluetooth scanner: MUST BE INTEGER!\t'))

	sensor=SimulatedBluetoothScan(str(roomID),True)

	consec_e=0
	count=1
	while True and consec_e<3:
		if count==4:
			#print("Go back to 1")
			count=1
		try:
			body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'sim_bl_sensor_'+roomID, 'category':'publisher','field':'bluetooth'}
			r=requests.put('http://'+str(sensor.catalogAddress)+':'+str(sensor.catalogPort),json=body)
			time_sleep=r.json()['timeToSleep']
			newIpBroker=r.json()['ipBroker']
			newPortBroker=r.json()['portBroker']
			sensor.toSense=r.json()['toSense']
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
				if count==3 and sensor.ipMessageBroker!="" and sensor.portMessageBroker!="":
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



