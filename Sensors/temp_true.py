import paho.mqtt.client as PahoMQTT
import time
import RPi.GPIO as GPIO
import dht11
import datetime
import json
import random
import socket
import requests

class MyPublisher:
	"""sensore raspberry"""
	def __init__(self, clientID):#,broker):
		self.clientID = clientID
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect

		###CATALOG
		file_content=json.load(open('confFileTemp.json'))
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
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, message, 2)
		print("Published under topic %s"%topic)
		print(message)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

	def updateBroker(self,broker):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

		self.messageBroker=broker

		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()

		print(f"Broker has changed to {self.messageBroker}!")


if __name__ == "__main__":
	# initialize GPIO
	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)

	sensor = MyPublisher("MyPublisher_temp")
	buildingID='SmartMuseum'
	roomID=str(1)
	s="t" 
	count_exc_avviamento=0
	ok=False

	while True and count_exc_avviamento<3 and ok==False:

		try:
			body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'true_temp_sensor_'+roomID, 'category':'publisher','field':'temp'}
			r=requests.put('http://'+str(sensor.catalogAddress)+':8080',json=body)
			time_sleep=r.json()['timeToSleep']
			sensor.messageBroker=r.json()['broker']
			print("Sensor inserted in catalog!")
			sensor.start()
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
		no_incr=False
		while True and consec_e<3:
			if count==13:
				count=1
			print(count)

			try:
				body={'whatPut':1,'IP':sensor.address,'port':False, 'last_update':0, 'whoIAm':'true_temp_sensor_'+roomID, 'category':'publisher','field':'temp'}
				r=requests.put('http://'+str(sensor.catalogAddress)+':8080',json=body)
				time_sleep=r.json()['timeToSleep']
				newbroker=r.json()['broker']
				if newbroker!=sensor.messageBroker:
					sensor.updateBroker(newbroker)
				print("Sensor updated in catalog!")
				if count==12:

					print("time to publish")

					instance = dht11.DHT11(pin=17)

					result = instance.read()

					if result.is_valid():

						temp= int(result.temperature)
						local_time=datetime.datetime.now()
						date=local_time.strftime('%d-%m-%Y %H:%M:%S')
						message={
							"room": "1",
							"value": temp, 
							"timestamp": date,	
						}
						print("ready to publish")
						sensor.myPublish ('SmartMuseum/'+roomID+'/t', json.dumps(message))
					else:
						print("something went wrong.. try to publish at next iteration")
						no_incr=True
				consec_e=0

			except requests.exceptions.RequestException as e:
				print(e)
				consec_e+=1
				print("Error. Go to sleep for 5 seconds, then retry...")
				time_sleep=5

			finally:
				if no_incr==False:
					count=count+1
				no_incr=False
				time.sleep(time_sleep)

		print("Catalog seems to be down... killing process...")	
		time.sleep(3)	
		exit()

	else:
		print("Cannot find active catalog... killing process...")
		time.sleep(3)
		exit()
