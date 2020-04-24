import requests
import threading
import json

class GetWithThread(threading.Thread):
	def __init__ (self, typeOfRequest,link,DBAddress,DBPort):
		threading.Thread.__init__(self)
		self.typeOfRequest=typeOfRequest
		self.link=link
		self.DBAddress=DBAddress
		self.DBPort=DBPort

	def run(self):
		#print("Started Process!")
		self.printAndUpdate(self.typeOfRequest,self.link,self.DBAddress,self.DBPort)		
		print("Updated {}!".format(self.typeOfRequest))
		return True

	def createAnswer(self,listOfTemperatures):
		dictionaryTemperatures={}
		for item in listOfTemperatures:
			#If the room still wasn't present, add it
			if item[1] not in dictionaryTemperatures:
				dictionaryTemperatures[item[1]]={}
				#Once created an object to store into the dictionary, create two lists and append temperature value + datetime
				dictionaryTemperatures[item[1]]['all']=[]
				dictionaryTemperatures[item[1]]['all'].append(item[2])
				dictionaryTemperatures[item[1]]['dates']=[]
				dictionaryTemperatures[item[1]]['dates'].append(item[3])

			else :
				#If it was already present, just append the last relevation
				dictionaryTemperatures[item[1]]['all'].append(item[2])
				dictionaryTemperatures[item[1]]['dates'].append(item[3])

		for item in dictionaryTemperatures:
				#For each key (room), evaluate some easy statistics!
				dictionaryTemperatures[item]['avg']=round(sum(dictionaryTemperatures[item]['all']) / len(dictionaryTemperatures[item]['all']),2)
				dictionaryTemperatures[item]['max']=max(dictionaryTemperatures[item]['all'])
				dictionaryTemperatures[item]['min']=min(dictionaryTemperatures[item]['all'])
				dictionaryTemperatures[item]['lastRelevation']=max(dictionaryTemperatures[item]['dates'])

		return dictionaryTemperatures	

	def printAndUpdate(self,typeOfRequest,link,DBAddress,DBPort):
		try:
			rdb=requests.get('http://'+str(DBAddress)+':'+str(DBPort)+'/temperatures?typeOfRequest='+typeOfRequest)
			if rdb.json()["value"]!=False and rdb.json()["value"]!=[]:
				listOfTemperatures=rdb.json()["value"]
				dictionaryTemperatures=self.createAnswer(listOfTemperatures)
				for room in dictionaryTemperatures: 
					avg=dictionaryTemperatures[room]['avg']
					top=dictionaryTemperatures[room]['max']
					und=dictionaryTemperatures[room]['min']
					last_time=str(dictionaryTemperatures[room]['lastRelevation'])
					#print(last_time)
					last_index=list(dictionaryTemperatures[room]['dates']).index(last_time)
					#print(last_index)
					last=dictionaryTemperatures[room]['all'][last_index]
					#print(last_temp)
					body={'room':str(room),'max':str(top), 'min':str(und), 'avg':str(avg), 'last':str(last)}
					#print("w")
					#print(body)
					try:
						p=requests.post('http://dweet.io/dweet/for/'+str(link),json=body)
					#Exception for the postRequest
					except Exception as e:
						try:
							print("Status code: "+str(p.status_code))
							print("Status code: "+str(p.reason))
						except:pass
						print(e)	
			else:
				print("No available data for {}!".format(self.typeOfRequest))
		#Exception for the getRequest
		except Exception as e:
			try:
				print("Status code: "+str(rdb.status_code))
				print("Status code: "+str(rdb.reason))
			except:pass
			print(e)	
