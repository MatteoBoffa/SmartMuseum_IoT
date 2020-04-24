import paho.mqtt.client as PahoMQTT
import time
import RPi.GPIO as GPIO
import dht11
import datetime
import json
import random
from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral
import requests
import socket

#import classes as c

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

class BluetoothScan():
	def __init__(self, clientID):#,broker):
		self.clientID = clientID

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect

		file_content=json.load(open('confFileBl.json'))
		self.catalogAddress=file_content.get('ipCatalog')
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		self.address=s.getsockname()[0]

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message):
		self._paho_mqtt.publish(topic,message, 2)
		print("Published under topic %s"%topic)
		print(message)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print("Connected to %s with result code: %d" % (self.messageBroker, rc))

	def updateBroker(self,broker):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()
		self.messageBroker=broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()
		print(f"Broker has changed to {self.messageBroker}!")

if __name__ == '__main__':
	
	sensor = BluetoothScan("BlScan_raspberry") 
	roomID=str(1)
	count_exc_avviamento=0
	ok=False
	while True and count_exc_avviamento<3 and ok==False:

		try:
			body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'true_bl_sensor_'+roomID, 'category':'publisher', 'field':'bluetooth'}
			r=requests.put('http://'+str(sensor.catalogAddress)+':8080',json=body)
			time_sleep=r.json()['timeToSleep']
			sensor.messageBroker=r.json()['broker']
			toSense=r.json()['toSense']
			print("Sensor inserted in catalog!")
			sensor.start()
			print("True Raspberry placed in room "+ str(roomID) +" and active for Bluetooth scan") 
			ok=True

		except requests.exceptions.RequestException as e:
			count_exc_avviamento+=1
			print(e)
			print("Error in contacting the catalog. Go to sleep for 5 seconds, then retry...")
			time_sleep=5

		finally:
			time.sleep(time_sleep)

	if count_exc_avviamento<3:

		consec_e=0
		count=1
		while True and consec_e<3:
			if count==7:
				count=1
			try:
				body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'true_bl_sensor_'+roomID, 'category':'publisher','field':'bluetooth'}
				r=requests.put('http://'+str(sensor.catalogAddress)+':8080',json=body)
				time_sleep=r.json()['timeToSleep']
				newbroker=r.json()['broker']
				toSense=r.json()['toSense']
				if newbroker!=sensor.messageBroker:
					sensor.updateBroker(newbroker)
				print("Sensor updated in catalog!")
				if count==6:
				
					#scanning
					scanner = Scanner().withDelegate(ScanDelegate())
					devices = scanner.scan(5.0)

					tosend=[]

					for dev in devices:
					   
					    if dev.addr in toSense:
					    	mac=dev.addr
					    	tosend.append(mac)

					if tosend:

					    local_time = datetime.datetime.now()
					    date=local_time.strftime('%d-%m-%Y %H:%M:%S')
					    msg={
			                 "room":1,
					      	 "value":tosend,
					    	 "timestamp":date,
					    }
					    sensor.myPublish('SmartMuseum/'+str(roomID)+'/b', json.dumps(msg))
				consec_e=0

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

	else:
		print("Cannot find active catalog... killing process...")
		time.sleep(3)
		exit()

