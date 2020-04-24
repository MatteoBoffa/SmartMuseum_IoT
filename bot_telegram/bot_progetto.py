import requests
import cherrypy
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,Message,InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
						  ConversationHandler, CallbackQueryHandler)
import logging
import socket
import json
import socket
import time
import sub.functions_bot as fb

PAINTER,PATH, PATH2, VISIT, INFO, POPULAR_PATHS=range(6)

class TelegramRest(object):
	exposed=True
	def __init__(self):
		pass
		
	def GET(self, *uri, **params):
		if len(list(params.values()))!=4 or list(params.keys())[0]!="ipWhereIAm" \
		or list(params.keys())[1]!="portWhereIAm" or list(params.keys())[2]!="ipGeneratePath" \
		or list(params.keys())[3]!="portGeneratePath":
			raise cherrypy.HTTPError(400, "ERROR: error with the parameters")
		else:
			telegram_bot.ipWhereIAm=str(params['ipWhereIAm'])
			telegram_bot.portWhereIAm=str(params['portWhereIAm'])
			telegram_bot.ipGeneratePath=str(params['ipGeneratePath'])
			telegram_bot.portGeneratePath=str(params['portGeneratePath'])
			
		requests.put('http://'+str(telegram_bot.catalogAddress)+':'+str(telegram_bot.catalogPort),json=body)



class TelegramRoom(object):
	exposed=True
	def __init__(self):
		self.rooms=[]
		pass
	def setRoom(self, room,chat_id):

		r={}
		r['room']=room
		r['chat_id']=str(chat_id)

		updated=False
		for old in self.rooms:
			if old['chat_id']==str(chat_id):
				#aggiorno
				old["room"]=room
				updated=True
		if updated==False:
			self.rooms.append(r)

	def getRoom(self, chat_id):
		found=False

		for r in self.rooms:
			if r['chat_id']==str(chat_id):
				found=r['room']
				break

		return found

class TelegramBot(object):

	def __init__(self):
		file_content2=json.load(open('confFileBot.json'))
		pathInfo=json.load(open('sub/roomInfo.json'))
		self.roomInfo=json.load(open('sub/roomDescriptions.json'))
		
		self.catalogAddress=file_content2.get('ipCatalog')
		self.catalogPort=file_content2.get('catalogPort')
		self.token=file_content2.get('token')
		self.ipWhereIAm=''
		self.portWhereIAm=''
		self.ipGeneratePath=''
		self.portGeneratePath=''
		self.portTelegram=int(file_content2.get('telegramPort'))
		s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("localhost", 80))
		self.address=s.getsockname()[0]

	def start(self, update, context):

		reply_keyboard=[]
		body={'chat_id': update.effective_chat.id}
		temp=requests.get('http://'+str(self.catalogAddress)+':'+str(self.catalogPort)+'?chatToSearch='+str(update.effective_chat.id))
		print('++++\n\nStampo la get \n\n')
		print(temp.json())
		if temp.json()!=False:
			temp=temp.json()
			for t in temp['values']:
				a=str(t)[2:len(t)-3]
				print(a)
				reply_keyboard.append([InlineKeyboardButton(a, callback_data=a)])
			reply_markup=InlineKeyboardMarkup(reply_keyboard)
			update.message.reply_text('Hi {}! Welcome in our Smart Museum. You should now be in the entrance room. Are you ready to start the tour?'.format(update.message.from_user.first_name))
			context.bot.send_message(chat_id=update.effective_chat.id, text='Choose the name of the painter you got as guide', reply_markup=reply_markup, parse_mode='Markdown')
		
		else :
			update.message.reply_text('Hi {}| There was an error, you are alread in the system!'.format(update.message.from_user.first_name))
			self.error()
		return PAINTER

	def unknown(self, update, context):
		context.bot.send_message(chat_id=update.effective_chat.id, text='I could not understand the command you typed. For this bot all you need to do is to push the buttons in the chat. If you want to cancel the session type /cancel.\n You wrote: {}'.format(update.message.text))
		
	def error(self, update, context):
		logger = logging.getLogger(__name__)
		logger.warning('Update "%s" caused error "%s"', update, context.error)

	def cancel(self, update, context):
		logger = logging.getLogger(__name__)
		user = update.message.from_user
		body={'whatPut':3, 'chat_id': update.effective_chat.id}
		requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
		logger.info("User %s canceled the conversation.", user.first_name)
		update.message.reply_text('Bye! I hope we can talk again some day.',
								  reply_markup=ReplyKeyboardRemove())

		return ConversationHandler.END

	def getPainter(self, update,context):
		query = update.callback_query
		print(query.data)
		body={'whatPut': 2,'choice': query.data, 'chat_id': update.effective_chat.id}
		requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
		keyboard = [[InlineKeyboardButton("Find Popular Paths", callback_data='paths'),
					InlineKeyboardButton("Begin Visit", callback_data='visit')
					],
					[InlineKeyboardButton("Exit Visit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=update.effective_chat.id, text='Please welcome {}, will be your guide! \n Now you should make a choice!'.format(query.data))
		context.bot.send_message(chat_id=update.effective_chat.id, text='You can: \n Find out *most popular paths*, if you want to organize your visit.\n *Begin* right away the visit. \n *Exit* the visit ', reply_markup=reply_markup, parse_mode='Markdown')
		return PATH

	def helpButton(self, update, context):
		user=update.message.from_user
		keyboard = [[InlineKeyboardButton("Find Popular Paths", callback_data='paths'),
					InlineKeyboardButton("Begin Visit", callback_data='visit')
					],
					[InlineKeyboardButton("Exit Visit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=update.effective_chat.id, text='You can: \n Find out *most popular paths*, if you want to organize your visit.\n *Begin* right away the visit. \n *Exit* the visit ', reply_markup=reply_markup, parse_mode='Markdown')
		return PATH 


	def pathChoice(self, update, context):
		query = update.callback_query
		if query.data=='paths':
			print('I\'m in paths')
			keyboard = [[InlineKeyboardButton("Quick Visit", callback_data='quick'),
					InlineKeyboardButton("Medium Visit", callback_data='medium')
					],
					[InlineKeyboardButton("Long Visit", callback_data='long')]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			context.bot.send_message(chat_id=update.effective_chat.id, text='To know the popular path right for you I have one question: how long should your visit be?', reply_markup=reply_markup, parse_mode='Markdown')
			return PATH2

		if query.data=='visit':
			print('I\'m in visit')
			keyboard = [[InlineKeyboardButton("Check My Position", callback_data='position'),
					],
					[InlineKeyboardButton("Exit", callback_data='exit')]]
			reply_markup = InlineKeyboardMarkup(keyboard)
			context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to the visit we are about to start! Let me give you some brief instructions.')
			pass
			time.sleep(1)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='To know where you are, I need you to push the button *Check My Position*. \n It is extremely important, so I can send you the right information!', parse_mode='Markdown')
			pass
			time.sleep(2)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='If you want more information, click on *Tell me more*',parse_mode='Markdown')
			pass
			time.sleep(1)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='When you want to end your visit, simply push *Exit*.', parse_mode='Markdown')
			pass
			time.sleep(1)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='Hope everything\'s clear! Let\'s start!', reply_markup=reply_markup)
			return VISIT

		if query.data=='exit':

			body={'whatPut':3, 'chat_id': update.effective_chat.id}
			requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
			context.bot.send_message(chat_id=update.effective_chat.id, text='Bye! I hope the visit went well! Have a good day.', reply_markup=ReplyKeyboardRemove())
			return ConversationHandler.END



	def paths2(self, update, context):
		paths=[]
		address_path=self.ipGeneratePath
		port_path=self.portGeneratePath
		query = update.callback_query
		keyboard = [[InlineKeyboardButton("Find Popular Paths", callback_data='paths'),
					InlineKeyboardButton("Begin Visit", callback_data='visit')],
					[InlineKeyboardButton("Exit Visit", callback_data='exit')]]
		try:
			rdb=requests.get('http://'+str(address_path)+':'+str(port_path)+"?duration=30")
			if rdb.json()['value']!=False and rdb.json()['value']!=[]:
				print(rdb.text)
				result=rdb.json()['value']
				sorted_d=result['roomsScores']
				maxScore=result['maxScore']
				finalPath=result['finalPath']
				print("With the following rooms' scores:")
				for key in sorted_d:
					print("Room "+str(key)+": "+str(sorted_d[key]))
					print("The maximum score is "+str(maxScore))
					print("Taking the following path: ")
				for element in finalPath:
					print("- Room "+str(element))

			elif rdb.json()['value']==[]:
					self.error(update,context)
					print("No data avaiable")
					reply_markup = InlineKeyboardMarkup(keyboard)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup, parse_mode='Markdown')
				
					return PATH
		
			else:
					self.error(update,context)
					print("Error: something went wrong with your request. Try again!")
					reply_markup = InlineKeyboardMarkup(keyboard)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup, parse_mode='Markdown')

					return PATH

		except Exception as e:
			try:
				self.error(update,context)
				reply_markup = InlineKeyboardMarkup(keyboard)
				context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup, parse_mode='Markdown')
				print("Status code: "+str(rdb.status_code))
				print("Status code: "+str(rdb.reason))
				return PATH
			except:
				pass
				print(e)
				return PATH

		stop_it=int(len(sorted_d))
		if (query.data)=='quick':
			stop_it=int(len(sorted_d)/2)-1
			if stop_it<1:
				stop_it=1
		elif (query.data)=='medium':
			stop_it=int(len(sorted_d)/2)+1
		elif (query.data)=='long':
			stop_it=int((len(sorted_d)))

		if stop_it!=1:
			context.bot.send_message(chat_id=update.effective_chat.id, text='For a {} I suggest {} rooms. Let me check the most popular ones.'.format(query.data, stop_it))
			pass
			time.sleep(2)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='So, you should see in this order:')
		else:
			context.bot.send_message(chat_id=update.effective_chat.id, text='For a {} I suggest {} room. Let me check the most popular one.'.format(query.data, stop_it))
			pass
			time.sleep(2)
			pass
			context.bot.send_message(chat_id=update.effective_chat.id, text='So, you should see the:')

		it=1
		for key in sorted_d:
			if it<=stop_it:
				room_id=int(key)
				right_room=[]
				right_room=fb.extractRightRoom(self.roomInfo, room_id)
				time.sleep(1)
				context.bot.send_message(chat_id=update.effective_chat.id, text='*{}* Room'.format(right_room['name']), parse_mode = "Markdown")
				it=it+1
			else: 
				pass
		keyboard = [[InlineKeyboardButton("Find Popular Paths", callback_data='paths'),
					InlineKeyboardButton("Begin Visit", callback_data='visit')],
					[InlineKeyboardButton("Exit Visit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=update.effective_chat.id, text='What do you want to do now?')
		context.bot.send_message(chat_id=update.effective_chat.id, text='You can: \n Find out other popular paths.\n *Begin* right away the visit. \n *Exit* the visit ', reply_markup=reply_markup, parse_mode='Markdown')
		return PATH
			

	def beginVisit(self, update, context):
		keyboard = [[InlineKeyboardButton("Check My Position", callback_data='position'),
					],
					[InlineKeyboardButton("Exit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to the visit we are about to start! Let me give you some brief instructions.')
		pass
		time.sleep(1)
		pass
		context.bot.send_message(chat_id=update.effective_chat.id, text='To know where you are, just push the button *Check My Position*. \n It is extremely important, so I can send you the right information!', parse_mode='Markdown')
		pass
		time.sleep(2)
		pass
		context.bot.send_message(chat_id=update.effective_chat.id, text='If you want more information, click on *Tell me more!*', parse_mode='Markdown')
		pass
		time.sleep(1)
		pass
		context.bot.send_message(chat_id=update.effective_chat.id, text='When you want to end your visit, simply push the *Exit* button.', parse_mode='Markdown')
		pass
		time.sleep(1)
		pass
		context.bot.send_message(chat_id=update.effective_chat.id, text='Hope everything is clear! Let\'s start!', reply_markup=reply_markup)
		return VISIT

	def visitButton(self, update, context):
		query = update.callback_query

		chat_string=update.effective_chat.id
		keyboard = [[InlineKeyboardButton("Check My Position", callback_data='position'), InlineKeyboardButton("Tell Me More", callback_data='info')],
								[InlineKeyboardButton("Exit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		keyboard_error = [[InlineKeyboardButton("Check My Position", callback_data='position'),],
							[InlineKeyboardButton("Exit", callback_data='exit')]]
		reply_markup_error = InlineKeyboardMarkup(keyboard_error)
		adress_position=self.ipWhereIAm
		port_position=self.portWhereIAm

		if query.data=='position':
			try:
				rdb=requests.get('http://'+str(adress_position)+':'+str(port_position)+"?chatId="+str(update.effective_chat.id))
				if rdb.json()['value']!=False and rdb.json()['value']!=[]:
					room=rdb.json()['value'][1]
					when=rdb.json()['value'][3]
					macEstimote=rdb.json()['value'][2]
					if isinstance(room, int) and isinstance(when, str) and isinstance(macEstimote, str):
						print("The searched person has the following mac-adress "+str(macEstimote))
						print("It was last seen at "+str(when))
						print("Last seen in room "+str(room))
						right_room=fb.extractRightRoom(self.roomInfo, str(room))
						print("Room name is:"+str(right_room['name']))
						telegram_room.setRoom(right_room, update.effective_chat.id)
						context.bot.send_message(chat_id=update.effective_chat.id, text='You are in {} room!'.format(right_room['name']))
						context.bot.send_message(chat_id=update.effective_chat.id, text='Please select what you want me to do:', reply_markup=reply_markup)
						return INFO
					else:
						print('Values are present but they are not right')
						self.error(update, context)
						context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
						return VISIT
				elif rdb.json()['value']==[]:
					print("No data avaiable")
					self.error(update, context)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
				else:
					print("Another error: unknown")
					self.error(update, context)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
			except Exception as e:
				try:
					print("Another error: something went wrong with your request. ")
					print("Status code: "+str(rdb.status_code))
					print("Reason: "+str(rdb.reason))
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
				except:
					print(e)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT

			return VISIT

		if query.data=='exit':
			body={'whatPut':3, 'chat_id': update.effective_chat.id}
			requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
			context.bot.send_message(chat_id=update.effective_chat.id, text='Bye! I hope the visit went well! Have a good day.', reply_markup=ReplyKeyboardRemove())
			return ConversationHandler.END


	def infoButton(self, update, context):
		keyboard = [[InlineKeyboardButton("Check My Position", callback_data='position'), InlineKeyboardButton("Tell Me More", callback_data='info')],
							[InlineKeyboardButton("Exit", callback_data='exit')]]
		reply_markup = InlineKeyboardMarkup(keyboard)
		keyboard_error = [[InlineKeyboardButton("Check My Position", callback_data='position'),],
							[InlineKeyboardButton("Exit", callback_data='exit')]]
		reply_markup_error = InlineKeyboardMarkup(keyboard_error)
		query=update.callback_query
		right_info=False
		if query.data=='info':
			right_info=telegram_room.getRoom(update.effective_chat.id) 
			if right_info==False:
				print('wrong info about room')
				return -1
			else: 
				context.bot.send_message(chat_id=update.effective_chat.id, text=right_info['info'])
				pass
				time.sleep(1)
				pass
				context.bot.send_message(chat_id=update.effective_chat.id, text=right_info['des'])
				pass
				time.sleep(2)
				pass
				context.bot.send_message(chat_id=update.effective_chat.id, text="To find out more follow this link: "+"["+right_info['link']+"]", parse_mode='Markdown')
				pass
				time.sleep(2)
				pass
				context.bot.send_message(chat_id=update.effective_chat.id, text="Please select what you want me to do:", reply_markup=reply_markup)
				return INFO

		if query.data=='position':

			adress_position=self.ipWhereIAm
			port_position=self.portWhereIAm
			try:
				rdb=requests.get('http://'+str(adress_position)+':'+str(port_position)+"?chatId="+str(update.effective_chat.id))
				if rdb.json()['value']!=False and rdb.json()['value']!=[]:
					room=rdb.json()['value'][1]
					when=rdb.json()['value'][3]
					macEstimote=rdb.json()['value'][2]
					if isinstance(room, int) and isinstance(when, str) and isinstance(macEstimote, str):
						print("The searched person has the following mac-adress "+str(macEstimote))
						print("It was last seen at "+str(when))
						print("Last seen in room "+str(room))
						right_room=fb.extractRightRoom(self.roomInfo, str(room))
						print("Room name is:"+str(right_room['name']))
						telegram_room.setRoom(right_room, update.effective_chat.id)
						context.bot.send_message(chat_id=update.effective_chat.id, text='You are in {} room!'.format(right_room['name']))
						context.bot.send_message(chat_id=update.effective_chat.id, text='Please select what you want me to do:', reply_markup=reply_markup)
						return INFO
					else:
						print('Values are present but they are not right')
						self.error(update, context)
						context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
						return VISIT
				elif rdb.json()['value']==[]:
					print("No data avaiable")
					self.error(update, context)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
				else:
					print("Another error: unknown")
					self.error(update, context)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
			except Exception as e:
				try:
					print("Another error: something went wrong with your request. ")
					print("Status code: "+str(rdb.status_code))
					print("Reason: "+str(rdb.reason))
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT
				except:
					print(e)
					context.bot.send_message(chat_id=update.effective_chat.id, text='Hey, an error occoured. Wait a little bit, try again, or contact directly staff for support. \nTo try again, push one of the buttons below!', reply_markup=reply_markup_error, parse_mode='Markdown')
					return VISIT

		if query.data=='exit':
			body={'whatPut':3, 'chat_id': update.effective_chat.id}
			requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
			context.bot.send_message(chat_id=update.effective_chat.id, text='Bye! I hope the visit went well! Have a good day.', reply_markup=ReplyKeyboardRemove())
			return ConversationHandler.END

	def exitVisit(self, update, context):
		body={'whatPut':3, 'chat_id': update.effective_chat.id}
		requests.put('http://'+str(self.catalogAddress)+':'+str(self.catalogPort),json=body)
		context.bot.send_message(chat_id=update.effective_chat.id, text='Bye! I hope the visit went well! Have a good day.', reply_markup=ReplyKeyboardRemove())
		return ConversationHandler.END


	def main(self):
		updater=Updater(self.token, use_context=True)
		disp=updater.dispatcher
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
		logger = logging.getLogger(__name__)
		conv_handler = ConversationHandler(
			entry_points=[CommandHandler('start', self.start)],

			states={

				PAINTER: [CallbackQueryHandler(self.getPainter)],
				PATH: [CallbackQueryHandler(self.pathChoice)],
				PATH2:[CallbackQueryHandler(self.paths2)],
				INFO: [CallbackQueryHandler(self.infoButton)],
				VISIT: [CallbackQueryHandler(self.visitButton)],
			},

			fallbacks=[CommandHandler('cancel', self.cancel)]
		)


		disp.add_handler(conv_handler)
		disp.add_handler(MessageHandler(Filters.all, self.unknown))
		updater.start_polling()
		updater.idle()


	
	
if __name__=='__main__':
	telegram_bot=TelegramBot()
	telegram_rest=TelegramRest()
	telegram_room=TelegramRoom()

	conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			}
		}

	
	cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': telegram_bot.portTelegram})
	cherrypy.tree.mount(telegram_rest, '/', conf)
	cherrypy.engine.start()
	body={'whatPut':1, 'IP':telegram_bot.address,'port':telegram_bot.portTelegram, 'last_update':0, 'whoIAm':'telegramBot', 'category':'server', 'field': ''}

	while True:
		try:
			requests.put('http://'+str(telegram_bot.catalogAddress)+':'+str(telegram_bot.catalogPort),json=body)
			telegram_bot.main()
		except requests.exceptions.RequestException as e:
			print(e)
	cherrypy.engine.exit()

