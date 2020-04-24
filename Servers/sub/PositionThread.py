import requests
import threading
import json
import datetime

class GetWithThread(threading.Thread):
	def __init__ (self, typeOfRequest,option,link1,link2,DBAddress,DBPort):
		threading.Thread.__init__(self)
		self.typeOfRequest=typeOfRequest
		self.option=option
		self.link1=link1
		self.link2=link2
		self.DBAddress=DBAddress
		self.DBPort=DBPort

	def run(self):
		#print("Started Process!")
		self.sendRequestAndUpdate(self.typeOfRequest,self.option,self.link1,self.link2,self.DBAddress,self.DBPort)		
		print("Updated {}!".format(self.typeOfRequest))
		return True

	def createAnswer(self,listOfPositions,option):
		dictionaryFirstUse={}
		dictionaryPositionMac={}
		dictionarySecondUse={}
		for item in listOfPositions:
			#Here I'm counting how many people have been registered in each room (multiple relevation possible)
			#For example, if for two consecutives relevations I'm registered on room 4, I'm counted twice
			if item[1] not in dictionaryFirstUse:
				dictionaryFirstUse[item[1]]=1
			else:
				dictionaryFirstUse[item[1]]=dictionaryFirstUse[item[1]]+1
		"""
		Here on the other hand I'm counting the relevation if:
		- It's the first relevation I'm receiving on that room
		- There was another in the past, but it was more than 10 minutes ago --> now set to 20 seconds, just to test!
		"""
		for item in listOfPositions:
			if str(item[1])+" "+item[2] not in dictionaryPositionMac:
				if str(item[1]) not in dictionarySecondUse:
					dictionarySecondUse[str(item[1])]=1
				else:
					dictionarySecondUse[str(item[1])]+=1
				dictionaryPositionMac[str(item[1])+" "+item[2]]=item[3]
			else:
				lastDate=datetime.datetime.strptime(dictionaryPositionMac[str(item[1])+" "+item[2]],'%Y-%m-%d %H:%M:%S')
				date=datetime.datetime.strptime(item[3],'%Y-%m-%d %H:%M:%S')
				difference=date-lastDate
				minutes=difference.days*24*60+difference.seconds/60
				if minutes>=10:
					dictionarySecondUse[str(item[1])]=dictionarySecondUse[str(item[1])]+1
		realTimePositioning={}
		if option==1:
			for item in listOfPositions:
				time=datetime.datetime.strptime(item[3],'%Y-%m-%d %H:%M:%S')
				if str(item[2]) not in realTimePositioning:
					realTimePositioning[str(item[2])]=[item[1], item[3]]
				else:
					time2=datetime.datetime.strptime(realTimePositioning[str(item[2])][1],'%Y-%m-%d %H:%M:%S')				
					if time2<time:
						realTimePositioning[str(item[2])]=[item[1], item[3]]
		return dictionaryFirstUse, dictionarySecondUse, realTimePositioning

	def printingPart(self,statsWithRep,statsNoRep):	
		print("\n\nFirst results: ")
		print("- counting occurrencies of people on that room")
		for item in statsWithRep.keys():
			print("Room "+str(item)+" with "+str(statsWithRep[item])+" relevations")
		print("\n\nSecond results: ")
		print("- this time same people staying on the room are not allowed")
		for item in statsNoRep.keys():
			print("Room "+str(item)+" with "+str(statsNoRep[item])+" relevations")

	def sortingPart(self,statsWithRep):
		order=[]
		for item in statsWithRep.keys():
			pop=int(statsWithRep[item])
			order.append(pop)
		order.sort(reverse=True)
		toSend1=[]
		toSend2=[]
		for it in order:
			for it2 in statsWithRep.keys():
				if statsWithRep[it2]==it and it2 not in toSend1:
					toSend1.append(it2)
					toSend2.append(it)	
		return toSend1,toSend2

	def sendRequestAndUpdate(self,typeOfRequest,option,firstLink,secondLink,DBAddress,DBPort):
		try:
			rdb=requests.get('http://'+str(DBAddress)+':'+str(DBPort)+'/positions?typeOfRequest='+str(typeOfRequest))
			if rdb.json()["value"]!=False and rdb.json()["value"]!=[]:
				listOfPositions=rdb.json()["value"]
				dictionaryFirstUse,dictionarySecondUse,realTimePositioning=self.createAnswer(listOfPositions,option)
				toReturnFullPeriod = {"listOfResults":listOfPositions, "statsPerRoomRep":dictionaryFirstUse, "statsPerRoomNoRep":dictionarySecondUse, "realTimePositioning":realTimePositioning}
				listOfResults=toReturnFullPeriod["listOfResults"]
				statsWithRep=toReturnFullPeriod["statsPerRoomRep"]
				statsNoRep=toReturnFullPeriod["statsPerRoomNoRep"]
				realTimePositioning=toReturnFullPeriod["realTimePositioning"]
				#self.printingPart(statsWithRep,statsNoRep)
				toSend1,toSend2=self.sortingPart(statsWithRep)
				body={'nrooms': len(statsWithRep.keys()), 'value': toSend1,'scores':toSend2}
				#print("****")
				#print(body)
				#Exception for the postRequest
				try:
					p=requests.post('http://dweet.io/dweet/for/'+str(firstLink),json=body)
					#print(p)
				except Exception as e:
					try:
						print("Status code: "+str(p.status_code))
						print("Status code: "+str(p.reason))
					except:pass
					print(e)
				#print("Finished to send the primary data with TYPE: "+(typeOfRequest))
				toSend1,toSend2=self.sortingPart(statsNoRep)
				body={'nrooms': len(statsNoRep.keys()), 'value': toSend1,'scores':toSend2}
				#print("****")
				#print(body)
				#Exception for the postRequest
				try:
					p=requests.post('http://dweet.io/dweet/for/'+str(secondLink),json=body)
				except Exception as e:
					try:
						print("Status code: "+str(p.status_code))
						print("Status code: "+str(p.reason))
					except:pass
					print(e)
				#print("Finished to send the secondary data with TYPE: "+(typeOfRequest))
			else:
				print("No available data!")

		#Exception for the getRequest
		except Exception as e:
			try:
				print("Status code: "+str(rdb.status_code))
				print("Status code: "+str(rdb.reason))
			except:pass
			print(e)	
