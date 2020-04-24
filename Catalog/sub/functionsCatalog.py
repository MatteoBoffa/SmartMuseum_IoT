import time
import mysql.connector
import re
from datetime import datetime 

def addDevice(mycursor, conn, json_body, timestamp, port):
	sql = "INSERT INTO credentialsServer (ipServer, TCPPort, whoIAm, role, lastUpdate) VALUES (%s, %s, %s, %s, %s)"
	val= (json_body['IP'], port, json_body['whoIAm'],json_body['category'], timestamp )
	try:
		mycursor.execute(sql, val)
		conn.commit()
		#print ("Device added. It was a "+json_body['whoIAm'])
		if json_body['whoIAm']=='telegramBot':
			initializedTelegramBot(mycursor, conn)
		"""
		sql2="SELECT * FROM credentialsServer"
		try:
			mycursor.execute(sql2)
			myresult = mycursor.fetchall()
			print("RESULTS ARE: ")
			print(myresult)
		except Exception as e:
			print("FAILED")
		"""
	except Exception as e:
		conn.rollback()
		print("Problem inserting into db: " + str(e))
	conn.close()	

def updateDevice(mycursor, conn, json_body, timestamp):
	sql = "UPDATE credentialsServer SET lastUpdate='{}' WHERE whoIAm='{}'".format(timestamp,json_body['whoIAm'])
	try:
		mycursor.execute(sql)
		conn.commit()
		#print ("Device updated. It was a "+json_body['whoIAm'])
	except Exception as e:
		conn.rollback()
		print("Problem modifying db: " + str(e))
	conn.close()

def removeInactive(user,passwd, actualTime,updatingTime):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			now=actualTime
			sql_Select_Out= "SELECT whoIAm, TIMESTAMPDIFF(second,lastUpdate, '{}') as diffTime FROM credentialsServer WHERE TIMESTAMPDIFF(second,lastUpdate, '{}')>{}".format(now,now,updatingTime*3)
			try:
				mycursor1.execute(sql_Select_Out)
				myresult = mycursor1.fetchall()
				for ob in myresult:
					#print(ob[1])
					sql_Delete_query = "DELETE FROM credentialsServer WHERE whoIAm='{}';".format(ob[0])
					if ob[0]=='telegramBot':
						initializedTelegramBot(mycursor1, conn)
					try:
						mycursor1.execute(sql_Delete_query)
						conn.commit()
						#print("Eliminated device")
					except Exception as e:
						conn.rollback()
						print("Problem: something went wrong eliminating objects: " + str(e))
			except Exception as e:
				print("Could not select timestamp differences!: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))

def infoOnDevice(user, passwd,whoIAm):
	result1=""
	result2=""
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "SELECT ipServer, TCPPort FROM credentialsServer WHERE whoIAm='{}'".format(whoIAm)
			try:
				mycursor1.execute(sql)
				myresult = mycursor1.fetchall()
			except Exception as e:
				print("Problem selecting broker: " + str(e))
				return result1,result2
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		if len(myresult)==1:
			result1=myresult[0][0]
			result2=myresult[0][1]
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return result1,result2

def initializedTelegramBot(mycursor1, conn):
	try:
		
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "UPDATE estimotes SET avaiable=True, chatId=NULL"
			try:
				mycursor1.execute(sql)
				conn.commit()
				#print ("Devices updated. All avaiable")
			except Exception as e:
				conn.rollback()
				print("Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		#conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))

def removeTelegramBot(user,passwd):
	conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
	mycursor1=conn.cursor()
	sqlForm="USE credentials_Database"
	try:
		mycursor1.execute(sqlForm)
		
		#print(self.actualTime)
		sql_Delete_query = "DELETE FROM credentialsServer WHERE whoIAm='telegramBot';"
		try:
			mycursor1.execute(sql_Delete_query)
			conn.commit()
			#print("Eliminated device tb")
			conn.close()
		except Exception as e:
			conn.rollback()
			print("Problem: something went wrong eliminating objects: " + str(e))
			conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	initializedTelegramBot(mycursor1, conn)

def foundTelegramBot(user,passwd):
	toReturn0=False
	toReturn1=False
	toReturn2=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "SELECT ipServer, TCPPort FROM credentialsServer WHERE whoIAm='{}'".format('telegramBot')
			try:
				mycursor1.execute(sql)
				myresult = mycursor1.fetchall()
				if len(myresult)==1:
					toReturn0=True
					toReturn1=myresult[0][0]
					toReturn2=myresult[0][1]
				else:
					#COMMENTATO DA ME!!
					#print("TelegramBot not present yet!")
					pass
			except Exception as e:
				print("Problem selecting db foundTelegramBot: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn0,toReturn1,toReturn2

def updateOrNewInsert(user,passwd, json_body):
	result=-1
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			print(json_body["whoIAm"])
			sql = "SELECT ipServer, TCPPort FROM credentialsServer WHERE whoIAm='{}'".format(json_body["whoIAm"])
			try:
				mycursor1.execute(sql)
				myresult = mycursor1.fetchall()
			except Exception as e:
				print("Problem selecting info updateOrNewInsert: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		if len(myresult)!=1:
			result=0
		else:
			result=myresult[0]
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return result

def checkValidityPut(json_body):
	if list(json_body.keys())!=['whatPut','IP','port', 'last_update', 'whoIAm', 'category','field']:
		print("Error: incorrect keys!")
		return False
	pat = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
	test = pat.match(json_body['IP'])
	if not test:
		print("Error: IP adress's not following the correct format")
		return False
	if json_body['category']!='server' and json_body['category']!='database' and json_body['category']!='publisher' and json_body['category']!='broker': #forse serve controllare telegrambot
		print("Error: unknown category")
		return False							
	try:
		port=int(json_body['port'])
	except:
		print("Error: incorrect port's format")
		return False
	return port

def selectAvaiableEstimotes(user, passwd):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			#INVECE DI AFRE SELECT ALL HO MESSO SOLO NAME
			sql_Select_Out= "SELECT name FROM estimotes WHERE avaiable=True"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=[]
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def selectChatIdAlreadyPresent(user, passwd):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			#INVECE DI AFRE SELECT ALL HO MESSO SOLO NAME
			sql_Select_Out= "SELECT chatId FROM estimotes WHERE avaiable=False"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=[]
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def selectUnavaiableEstimotes(user, passwd):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql_Select_Out= "SELECT * FROM estimotes WHERE avaiable=False"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=[]
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def selectUnavaiableMacEstimotes(user, passwd):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql_Select_Out= "SELECT macEstimote FROM estimotes WHERE avaiable=False"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				#print(toReturn)
				if len(toReturn)==0:
					toReturn=False
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def searchForMacAdress(user, passwd, chatId):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql_Select_Out= "SELECT macEstimote FROM estimotes WHERE chatId='{}'".format(chatId)
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=False
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def occupyChosenEstimote(user, passwd, choice, chatId):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			print(chatId)
			sql = "UPDATE estimotes SET avaiable=False, chatId='{}' WHERE name='{}'".format(chatId, choice)
			try:
				mycursor1.execute(sql)
				conn.commit()
				#print ("Device updated. Occupied estimote named "+choice)
			except Exception as e:
				conn.rollback()
				print("Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))

def freeChosenEstimote(user, passwd, chatId):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "UPDATE estimotes SET avaiable=True, chatId='{}' WHERE chatId='{}'".format('',chatId)
			try:
				mycursor1.execute(sql)
				conn.commit()
				#print ("Device updated. liberated estimote")
			except Exception as e:
				conn.rollback()
				print("Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))	


#FUNZIONE CHE NON AVEVO VISTO E HO RIFATTO MA: MAI USATA PRIMA?? ANYWAY QUELLA NUOVA USA IL CONNECTOR NON USER E PASSWORD 
#COSI' PUO' ESSERE USATA ANCHE DA ADD DEVICE PERCHè NON CAPISCO IL MOTIVO MA IN QUESTA FUNZIONE IL CONNECTOER VIENE CREATO NEL CATALOG 
def freeEstimotes(user,passwd):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "UPDATE estimotes SET avaiable=True, chatId=''"
			try:
				mycursor1.execute(sql)
				conn.commit()
				#print ("Devices updated.")
			except Exception as e:
				conn.rollback()
				print("Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))	

def nameExist(user,passwd,choice):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql_Select_Out= "SELECT * FROM estimotes WHERE name='{}'".format(choice)
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=False
			except Exception as e:
				print("Query didn't succeed: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn	

def checkValidityEstimote(user,passwd,whatPut,choice,chat_id):
	toReturn=True
	if whatPut==2:		
		result=nameExist(user,passwd,choice)
		if result==False:
			print("Name doesn't exist!")
			toReturn=False
		
		listOfChatId=selectChatIdAlreadyPresent(user,passwd)
		print(listOfChatId)
		found=False
		for element in listOfChatId:
			if element[0]==str(chat_id):
				found=True
		if found==True and toReturn==True:
			print("That chat id already exists!")
			toReturn=False
		
		listOfAvaiable=selectAvaiableEstimotes(user,passwd)
		if listOfAvaiable==False:
			print("Query went wrong")
			toReturn=False
			return toReturn
		found=False
		for element in listOfAvaiable:
			if element[0]==choice:
				found=True
		if found==False and toReturn==True:
			print("Trying to occupy an already occupied estimote!")
			toReturn=False
	else:
		listOfUnavaiable=selectUnavaiableEstimotes(user,passwd)
		if listOfUnavaiable==False:
			print("Query went wrong")
			toReturn=False
			return toReturn
		found=False
		for element in listOfUnavaiable:
			if element[3]==str(chat_id):
				found=True
		if found==False:
			print("No estimote associated to the passed chat_id")
			toReturn=False

	return toReturn
