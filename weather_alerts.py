from websocket import create_connection
from urllib.request import urlopen
import json
from datetime import datetime
import requests as req
import http.client, urllib
import time

personal_token  = "personal_token"
tempest_ID      = "tempest_id"
station_id      = "station_id"
push_token      = "push_token"
user            = "user_id"

	
#Lets setup some default thresholds for our alerts
a_WW		 		= 15	#Alert if we get wind more than 15kms
a_RW		 		= 5		#Alert if we get 5mm or more of rain
a_TH 				= 30	#Alert if the temp gets above 30	
a_TL		 		= 5		#Alert if the temp gets above 30	
a_SC		 		= 5		#Alert if we get more than 5 lightning strikes in the last hour
a_WC 				= 5		#Alert if the windchill is 5 or lower
a_BV	 			= 2 	#Alert if battery level drops
a_UV 				= 6		#UV index alert
a_RA		 		= 1380	#This is a normal value
a_HH			 	= 95	#High and low values for humidity
a_HL		 		= 20	#Low humidity values
a_UV		 		= 6		#UV Warning

#Setup our Lists, the index counts should all match
NumonicList	= ['WW:','RW:','WC:','BV:','HH:','CW:','RA:','HU:','HL:','UV:']	
MsgList = ['Wind Warning:','Rain Warning:','Wind Chill Warning:','Battery Voltage Warning:','High Heat Warning:','Cold Warning:','Radiation Warning:','High Humidity Warning:','Low Humidity Warning:', 'High UV Index']		
Warning = ['km','mm','C','V','C','C','W/m^2','%','%','I']	
Thresholds = [a_WW,a_RW,a_WC,a_BV,a_TH,a_TL,a_RA,a_HH,a_HL, a_UV]
Operator = ['GT','GT','LT','LT','GT','LT','GT','GT','LT','GT']
thislist = []
messageList = []
msg = ""
mycounter = 0

#Defiine a function to send a notification, I've also used a warning jpg which you can use your own.
def SendNotification(Title):
	try:
		r = req.post("https://api.pushover.net/1/messages.json", data = {
		"token": push_token,
		"user": user,
		"message": "Weather Warning: " + '\n' + Title
		},
		files = {
			"attachment": ("warning.jpg", open(r"d:\python\weather\warning.jpg", "rb"), "image/jpeg")
		})
	except:
		pass


#Greater than function to check 
def getAlertGT(AlertList, Thresholds, Warning, MsgList, NumonicList):
	print(MsgList, 'AlertList:', AlertList , ' - Thresholds:', Thresholds)
	if AlertList >= Thresholds:
		newstring= NumonicList + str(AlertList)
		if newstring not in thislist:
			thislist.append(newstring)
			messageList.append(MsgList + Warning + '\n' )
	elif AlertList <= Thresholds:
		newstring= NumonicList + str(AlertList)
		if newstring in thislist: thislist.remove(newstring) 
	return messageList	

#Less than function to check
def getAlertLT(AlertList, Thresholds, Warning, MsgList, NumonicList):
	print(MsgList, 'AlertList:', AlertList , 'Thresholds:', Thresholds)
	if AlertList <= Thresholds:
		newstring = NumonicList + str(AlertList)
		if newstring not in thislist:
			thislist.append(newstring)
			messageList.append(MsgList + Warning  + '\n' )
	elif AlertList >= Thresholds:
		newstring = NumonicList + str(AlertList)
		if newstring in thislist: thislist.remove(newstring) 
	return messageList	
	
#Lets do some of the work and get the data and perform our checks	
def opensocket():
		websock = create_connection('wss://ws.weatherflow.com/swd/data?api_key=' + personal_token)
		temp_rs =  websock.recv()
		websock.send('{"type":"listen_start",' + ' "device_id":' + tempest_ID + ',' + ' "id":"Tempest"}')
		temp_rs =  websock.recv()
		websock.close()


		#Read the json values into variables
		json_obj 		= json.loads(temp_rs)
		
		jWW 			= json_obj['obs'][0][3]
		jRW 			= json_obj['summary']['precip_total_1h']
		jWC	 			= json_obj['summary']['wind_chill']
		jFL	 			= json_obj['summary']['feels_like']
		jHH 			= json_obj['summary']['heat_index']
		jBV 			= json_obj['obs'][0][16]
		jUV 			= int(json_obj['obs'][0][10] or 0)
		jHU 			= json_obj['obs'][0][8]
		jRT		 		= json_obj['obs'][0][18]
		jLX 			= int(json_obj['obs'][0][9] or 0)
		jRA	 			= int(json_obj['obs'][0][11] or 0)
		jSC		 		= json_obj['obs'][0][15]

		AlertList	= [jWW,jRW,jWC,jBV,jHH,jHH,jRA,jHU,jHU,jUV]	
				
		for a, b, c, d, e, f in zip(AlertList, MsgList, Warning, Thresholds, Operator, NumonicList):
			if e == "GT":
				msg = getAlertGT(a, d, c, b, f)
			elif e == "LT":
				msg = getAlertLT(a, d, c, b, f)
			else:
				print('Somthing else here')

		if len(messageList) > 0:
			SendNotification(msg)

	
while True:
	mycounter+=1
	opensocket()
	print('sleeping')
	print(mycounter)
	time.sleep(20)
