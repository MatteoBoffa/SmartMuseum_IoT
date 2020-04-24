
import requests

def extractInfoRoom(roomInfo):
	info=[]
	for room in roomInfo:
				info_dict={}
				info_dict['id']=room['id']
				info_dict['nPaintings']=room['nPaintings']
				info_dict['artists']=room['artists']
				info_dict['info']=room['infoRoom']
				info_dict['des']=room['description']
				info_dict['link']=room['linkforInfo']
				info_dict['name']=room['name']
				info.append(info_dict)
	return info

def extractRightRoom(roomInfo, room_id):
	print('I\'m into extract')
	info=[]
	for room in roomInfo:
				info_dict={}
				info_dict['id']=room['id']
				info_dict['nPaintings']=room['nPaintings']
				info_dict['artists']=room['artists']
				info_dict['info']=room['infoRoom']
				info_dict['des']=room['description']
				info_dict['link']=room['linkforInfo']
				info_dict['name']=room['name']
				info.append(info_dict)
	print('I did everything for info')
	right_room=[]
	for el in info:
		if int(el['id'])==int(room_id):
			right_room=el
	return right_room
SAVED_ROOM=False

	