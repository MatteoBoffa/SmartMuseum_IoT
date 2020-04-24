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
		if json_body['whoIAm']=='telegramBot':
			initializedTelegramBot(mycursor, conn)
	except Exception as e:
		conn.rollback()
		print("Problem with the 'addDevice' function: " + str(e))
	conn.close()	

def updateDevice(mycursor, conn, json_body, timestamp):
	sql = "UPDATE credentialsServer SET lastUpdate='{}' WHERE whoIAm='{}'".format(timestamp,json_body['whoIAm'])
	try:
		mycursor.execute(sql)
		conn.commit()
	except Exception as e:
		conn.rollback()
		print("Problem with the 'updateDevice' function: " + str(e))
	conn.close()

def removeInactive(user,passwd, actualTime,updatingTime):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			now=actualTime
			sql_Select_Out= "SELECT whoIAm, TIMESTAMPDIFF(second,lastUpdate, '{}') as diffTime FROM credentialsServer \
			WHERE TIMESTAMPDIFF(second,lastUpdate, '{}')>{}".format(now,now,updatingTime*3)
			try:
				mycursor1.execute(sql_Select_Out)
				myresult = mycursor1.fetchall()
				for ob in myresult:
					sql_Delete_query = "DELETE FROM credentialsServer WHERE whoIAm='{}';".format(ob[0])
					if ob[0]=='telegramBot':
						initializedTelegramBot(mycursor1, conn)
					try:
						mycursor1.execute(sql_Delete_query)
						conn.commit()
					except Exception as e:
						conn.rollback()
						print("Problem with the 'removeInactive': something went wrong eliminating objects: " + str(e))
			except Exception as e:
				print("Problem with the 'removeInactive': Could not select timestamp differences!: " + str(e))
		except Exception as e:
			print("Problem with the 'removeInactive': Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'removeInactive': " + str(err))

def infoOnDevice(user, passwd, whoIAm):
	#Third parameter is the one that tells me who I actually searching
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
				print("Problem with the function 'infoOnDevice': Problem selecting broker: " + str(e))
				return result1,result2
		except mysql.connector.Error as err:
			print("Problem with the function 'infoOnDevice': Something went wrong: {}".format(err))
		if len(myresult)==1:
			result1=myresult[0][0]
			result2=myresult[0][1]
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the function 'infoOnDevice': " + str(err))
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
				print("Problem with the function 'initializedTelegramBot': Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the function 'initializedTelegramBot': {}".format(err))
		#conn.close()
	except mysql.connector.Error as err:
		print("Problem with the function 'initializedTelegramBot': " + str(err))
		
def removeTelegramBot(user,passwd):
	conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
	mycursor1=conn.cursor()
	sqlForm="USE credentials_Database"
	try:
		mycursor1.execute(sqlForm)
		sql_Delete_query = "DELETE FROM credentialsServer WHERE whoIAm='telegramBot';"
		try:
			mycursor1.execute(sql_Delete_query)
			conn.commit()
			conn.close()
		except Exception as e:
			conn.rollback()
			print("Problem with the function 'removeTelegramBot': something went wrong eliminating objects: " + str(e))
			conn.close()
	except mysql.connector.Error as err:
		print("Problem with the function 'removeTelegramBot': " + str(err))
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
			except Exception as e:
				print("Problem selecting db foundTelegramBot: " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the function 'foundTelegramBot': {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the function 'foundTelegramBot': " + str(err))
	return toReturn0,toReturn1,toReturn2

def updateOrNewInsert(user,passwd, json_body):
	result=-1
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql = "SELECT ipServer, TCPPort FROM credentialsServer WHERE whoIAm='{}'".format(json_body["whoIAm"])
			try:
				mycursor1.execute(sql)
				myresult = mycursor1.fetchall()
			except Exception as e:
				print("Problem selecting info updateOrNewInsert: " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the function 'updateOrNewInsert': {}".format(err))
		if len(myresult)!=1:
			result=0
		else:
			result=myresult[0]
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the function 'updateOrNewInsert': " + str(err))
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
			sql_Select_Out= "SELECT name FROM estimotes WHERE avaiable=True"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=[]
			except Exception as e:
				print("Problem with the 'selectAvaiableEstimotes': Query didn't succeed: " + str(e))
		except Exception as e:
			print("Problem with the 'selectAvaiableEstimotes': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'selectAvaiableEstimotes': " + str(err))
	return toReturn

def selectChatIdAlreadyPresent(user, passwd):
	#Function used for checking the validity of a new request for the estimotes
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE credentials_Database"
		try:
			mycursor1.execute(sqlForm)
			sql_Select_Out= "SELECT chatId FROM estimotes WHERE avaiable=False"
			try:
				mycursor1.execute(sql_Select_Out)
				toReturn = mycursor1.fetchall()
				if len(toReturn)==0:
					toReturn=[]
			except Exception as e:
				print("Problem with the 'selectChatIdAlreadyPresent':Query didn't succeed: " + str(e))
		except Exception as e:
			print("Problem with the 'selectChatIdAlreadyPresent': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'selectChatIdAlreadyPresent': " + str(err))
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
				print("Problem with the 'selectUnavaiableEstimotes': Query didn't succeed: " + str(e))
		except Exception as e:
			print("Problem with the 'selectUnavaiableEstimotes': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'selectUnavaiableEstimotes': " + str(err))
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
				print("Problem with the 'selectUnavaiableMacEstimotes': Query didn't succeed: " + str(e))
		except Exception as e:
			print("Problem with the 'selectUnavaiableMacEstimotes': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'selectUnavaiableMacEstimotes': " + str(err))
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
				print("Problem with the 'searchForMacAdress': Query didn't succeed: " + str(e))
		except Exception as e:
			print("Problem with the 'searchForMacAdress': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'searchForMacAdress': " + str(err))
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
			except Exception as e:
				conn.rollback()
				print("Problem with the 'occupyChosenEstimote': Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the 'occupyChosenEstimote': {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'occupyChosenEstimote': " + str(err))

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
				print("Problem with the 'freeChosenEstimote': " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the 'freeChosenEstimote': {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'freeChosenEstimote': " + str(err))	


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
				print("Problem with the 'freeEstimotes': Problem modifying db: " + str(e))
		except mysql.connector.Error as err:
			print("Problem with the 'freeEstimotes': {}".format(err))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'freeEstimotes': " + str(err))	

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
				print("Problem with the 'nameExist' " + str(e))
		except Exception as e:
			print("Problem with the 'nameExist': " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem with the 'nameExist': " + str(err))
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
