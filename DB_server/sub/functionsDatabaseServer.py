import time
import mysql.connector
import re
from datetime import datetime 

def addData(user,passwd, json_body, tableName):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE dataset_Database"
		toReturn=[]
		try:
			mycursor1.execute(sqlForm)
			if tableName=='temperatures':
				value='temperature'
			else:
				value="macEstimote"
			datetime_object = datetime.strptime(json_body['timestamp'], '%d-%m-%Y %H:%M:%S')
			sql_Insert = "INSERT INTO {} (room, {}, timestamp) VALUES (%s, %s, %s)".format(tableName, value)
			if tableName!="temperatures":
				for macAddress in json_body['value']:
					val= (json_body['room'], macAddress, datetime_object)
					try:
						mycursor1.execute(sql_Insert, val)
						conn.commit()
						print ("Info added. It was about "+tableName)
					except Exception as e:
						conn.rollback()
						print("Problem inserting into db: " + str(e))
			else:
				val= (json_body['room'], json_body['value'], datetime_object)
				try:
					mycursor1.execute(sql_Insert, val)
					conn.commit()
					print ("Info added. It was about "+tableName)
				except Exception as e:
					conn.rollback()
					print("Problem inserting into db: " + str(e))
		except Exception as e:
			print(e)
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))

def selectLastDay(user,passwd,tableName):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE dataset_Database"
		toReturn=[]
		now=datetime.now()
		if tableName=="positions":
			value="macEstimote"
		else:
			value="temperature"
		#RETURNING False IF PROBLEMS CONSULTING DATABASE
		#RETURNING EMPTY LIST IF NO RESULTS ARE AVAILABLE
		try:
			mycursor1.execute(sqlForm)
			sql_Select="SELECT id, room, {}, DATE_FORMAT(timestamp, '%Y-%m-%d %T')  FROM {}\
			 WHERE TIMESTAMPDIFF(HOUR,timestamp, '{}')<=24".format(value,tableName, now)
			try:
				mycursor1.execute(sql_Select)
				myresult = mycursor1.fetchall()	
				toReturn=myresult
			except Exception as e:
				print("Could not select items!: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()	
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def selectAll(user,passwd,tableName):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE dataset_Database"
		toReturn=[]
		now=datetime.now()
		if tableName=="positions":
			value="macEstimote"
		else:
			value="temperature"
		#RETURNING False IF PROBLEMS CONSULTING DATABASE
		#RETURNING EMPTY LIST IF NO RESULTS ARE AVAILABLE
		try:
			mycursor1.execute(sqlForm)
			sql_Select="SELECT id, room, {}, DATE_FORMAT(timestamp, '%Y-%m-%d %T')  FROM {}\
			 WHERE TIMESTAMPDIFF(HOUR,timestamp, '{}')<=48".format(value,tableName, now)
			try:
				mycursor1.execute(sql_Select)
				myresult = mycursor1.fetchall()	
				toReturn=myresult
			except Exception as e:
				print("Could not select items!: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()	
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def selectLastPosition(user,passwd, macEstimote):
	toReturn=False
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE dataset_Database"
		"""
		RETURNING:
		- Last occurrence --> if it exists and everything worked fine
		- None --> if no occurrences were found but the query worked (if results is not None per controllare)
		- False --> query andata male per qualche motivo
		"""
		now=datetime.now()
		try:
			mycursor1.execute(sqlForm)
			sql_Select="SELECT id, room, macEstimote, DATE_FORMAT(timestamp, '%Y-%m-%d %T') FROM positions\
			 WHERE macEstimote='{}' AND TIMESTAMPDIFF(MINUTE,timestamp, '{}')<=5 ORDER BY timestamp DESC".format(macEstimote, now)
			try:
				mycursor1.execute(sql_Select)
				myresult = mycursor1.fetchall()
				if len(myresult)>0:
					toReturn=myresult[0]
				else: 
					toReturn=None
			except Exception as e:
				print("Could not select the person desired!: " + str(e))
		except Exception as e:
			print("Could not execute the first query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))
	return toReturn

def removeOutOfDate(user,passwd, actualTime, deletionTime):
	try:
		conn=mysql.connector.connect(host="localhost", user=user, passwd=passwd)
		mycursor1=conn.cursor()
		sqlForm="USE dataset_Database"
		try:
			#SELECT TEMPERATURE OUT OF DATE
			mycursor1.execute(sqlForm)
			now=actualTime
			sql_Select_Out= "SELECT id, TIMESTAMPDIFF(second,timestamp, '{}') as diffTime FROM temperatures\
			 WHERE TIMESTAMPDIFF(HOUR,timestamp, '{}')>{}".format(now,now,deletionTime)
			try:
				mycursor1.execute(sql_Select_Out)
				myresult = mycursor1.fetchall()
				for ob in myresult:
					#DELETE TEMPERATURES OUT OF DATE
					sql_Delete_query = "DELETE FROM temperatures WHERE id='{}';".format(ob[0])
					try:
						mycursor1.execute(sql_Delete_query)
						conn.commit()
						print("Eliminated temperature data with id "+str(ob[0]))
					except Exception as e:
						conn.rollback()
						print("Problem: something went wrong eliminating objects: " + str(e))

			except Exception as e:
				print("Could not select timestamp differences!: " + str(e))
			
			#SELECT POSITIONS OUT OF DATE
			sql_Select_Out= "SELECT id, TIMESTAMPDIFF(second,timestamp, '{}') as diffTime FROM positions\
			 WHERE TIMESTAMPDIFF(HOUR,timestamp, '{}')>{}".format(now,now,deletionTime)
			try:
				mycursor1.execute(sql_Select_Out)
				myresult = mycursor1.fetchall()
				for ob in myresult:
					#DELETE POSITIONS OUT OF DATE
					sql_Delete_query = "DELETE FROM positions WHERE id='{}';".format(ob[0])
					try:
						mycursor1.execute(sql_Delete_query)
						conn.commit()
						print("Eliminated position data with id "+str(ob[0]))
					except Exception as e:
						conn.rollback()
						print("Problem: something went wrong eliminating objects: " + str(e))
			except Exception as e:
				print("Could not select timestamp differences!: " + str(e))
		except Exception as e:
			print("Could not perform the initial query!: " + str(e))
		conn.close()
	except mysql.connector.Error as err:
		print("Problem: something went wrong here!: " + str(err))

def checkValidityPut(user,passwd,json_body, tableName):
	"""
	CHECKING:
	-If the temperature is a temperature (type)
	-If the room is a room (type)
	-If the Mac has the correct format
	-If the datetime is actually a datetime (format again)
	"""
	if list(json_body.keys())!=['room','value','timestamp']:
		return False
	if tableName=='temperatures':
		try:
			temperature=float(json_body['value'])
			relevatedRoom=int(json_body['room'])
		except: 
			return False
	else:
		for macAddress in json_body['value']:
			#print(macAddress)
			pat = re.compile(r'(?:[0-9a-fA-F]:?){12}')
			test = pat.match(macAddress)
			if test is None:
				print("MAC DO NOT FIT")
				return False
			try:
				relevatedRoom=int(json_body['room'])
			except:
				print("ROOM DO NOT CAST")
				return False				
			#Part in which i check consistency of the data!
			"""
			- check if there's already an occurrance on the database (if there's no, no problem; if the query fails, error)
			- check if the last relevation has been done on a different room (if not, ok)
			- check that the second relevation is possible (less than 4 seconds means that the relevation is not consistent)
			"""
			lastRelevation=selectLastPosition(user,passwd, macAddress)
			if lastRelevation == False:
				print("QUERY TO THE DB FAILED")
				return False
			elif lastRelevation is not None:
				queryId,lastRoom, lastMac, lastTimestamp=lastRelevation
				if relevatedRoom!=lastRoom:
					now=datetime.now()
					lastTimestamp=datetime.strptime(lastTimestamp,'%Y-%m-%d %H:%M:%S')
					timestampDifference=now-lastTimestamp
					if timestampDifference.total_seconds()<=4:
						print("ERROR; INCONSISTENT DATA")
						return False

	pat = re.compile(r'[0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}')
	test = pat.match(json_body['timestamp'])
	if test is None:
		return False
	return True
