from websocket import create_connection
from urllib.request import urlopen
import json
from datetime import datetime
import requests as req
import http.client, urllib
import time

personal_token = "your personal token here"
tempest_ID = "your tempest id here"
station_id = "your station id here"
push_token = "your push token here"
user = "your user id here"

"""
The UV Index divides UV radiation levels into:
low (1-2)
moderate (3-5)
high (6-7)
very high (8-10)
extreme (11 and above).
"""

		
#Lets setup some defaults for our alerts. Setup your own values here
a_WW		 		= 15		#Alert if we get wind more than 15kms
a_RW		 		= 5		#Alert if we get 5mm or more of rain
a_TH 				= 30		#Alert if the temp gets above 30	
a_TL		 		= 1		#Alert if the temp gets below 1
a_SC		 		= 5		#Alert if we get more than 5 lightning strikes in the last hour
a_WC 				= 5		#Alert if the windchill is 5 or lower
a_BV	 			= 2 		#Alert if battery level drops
a_UV 				= 6  		#UV index alert
a_RA		 		= 1380		#This is a normal value
#a_HH			 	= 95		#High and low values for humidity
a_HL		 		= 20		#Low humidity values


#Lists
NumonicList	= ['WW:','RW:','WC:','BV:','HH:','CW:','RA:','HL:','UV:']	
MsgList = ['Wind Warning:','Rain Warning:','Wind Chill Warning:','Battery Voltage Warning:','High Heat Warning:','Cold Warning:','Radiation Warning:','Low Humidity Warning:', 'High UV Index']	
Warning = [' km',' mm',' C',' V',' C',' C',' W/m^2',' %',' I']	
Thresholds = [a_WW, a_RW, a_WC, a_BV, a_TH, a_TL, a_RA, a_HL,a_UV]
Operator = ['GT','GT','LT','LT','GT','LT','GT','LT','GT']
thislist = []
messageList = []
msg = ""
COUNT = 0
status = 'CLEAR'

def nonzero(value):
    if value == None:
        return 0
    return value

def listToString(s): 
    # initialize an empty string
    str1 = "" 
    # traverse in the string  
    for ele in s: 
        str1 += ele  
    # return string  
    return str1 	
	
def SendNotification(Title):
		r = req.post("https://api.pushover.net/1/messages.json", data = {
		"token": push_token,
		"user": user,
		"message": "Weather Warning: " + '\n' + Title
		},
		files = {
			"attachment": ("warning.jpg", open(r"d:\python\weather\warning.jpg", "rb"), "image/jpeg")
		})
counter = 0

def increment():
	global COUNT
	COUNT = COUNT +1
	return COUNT
	
def getAlert(AlertList, Thresholds, Warning, MsgList, NumonicList, operator):
	#Lets check if we have a warning
	if operator == "GT":
		if AlertList >= Thresholds:
			status = "WARNING"
			#Ok, We have breached our threshold add to the counter
			counter = increment()
			newstring= NumonicList + str(AlertList)
			#Now lets build the list. If the counter is 1 it's the first time so send the alert
			if counter == 1:
				thislist.append(newstring)
				messageList.append(status)
				messageList.append(MsgList + " " + str(AlertList) + Warning)
				messageList.append(counter)
			elif counter > 1:
				messageList.pop()
				messageList.append(counter)
		elif AlertList <= Thresholds:
			status = "CLEAR"
	else:
		if AlertList <= Thresholds:
			status = "WARNING"
			#Ok, We have breached our threshold add to the counter
			counter = increment()
			newstring= NumonicList + str(AlertList)
			#Now lets build the list. If the counter is 1 it's the first time so send the alert
			if counter == 1:
				thislist.append(newstring)
				messageList.append(status)
				messageList.append(MsgList + " " + str(AlertList) + Warning)
				messageList.append(counter)
			elif counter > 1:
				messageList.pop()
				messageList.append(counter)
		elif AlertList >= Thresholds:
			status = "CLEAR"
	output = "{:<19}Current: {:<12} Thresholds: {:<12} Status: {:<12}".format(MsgList, AlertList, Thresholds, status)
	print(output)
	return messageList		

def opensocket():
	try:
		#print('Opening Websocket connection...')
		websock = create_connection('wss://ws.weatherflow.com/swd/data?api_key=' + personal_token)
		temp_rs =  websock.recv()


		#print('Listening to Tempest endpoint...')
		websock.send('{"type":"listen_start",'       + ' "device_id":' + tempest_ID + ',' + ' "id":"Tempest"}')
		temp_rs =  websock.recv()

		#print('Receiving Tempest data...')
		temp_rs =  websock.recv()
		websock.close()
				
		#Read the json into variables
		json_obj 		= json.loads(temp_rs)
		jRW 			= json_obj['summary']['precip_total_1h']
		jWC	 		= json_obj['summary']['wind_chill']
		jFL	 		= json_obj['summary']['feels_like']
		jHH 			= json_obj['summary']['heat_index']
		jBV 			= json_obj['obs'][0][16]
		jUV 			= nonzero(json_obj['obs'][0][10])
		jHU 			= json_obj['obs'][0][8]
		jRT		 	= json_obj['obs'][0][18]
		jLX 			= nonzero(json_obj['obs'][0][9])
		jRA	 		= nonzero(json_obj['obs'][0][11])
		jSC		 	= json_obj['obs'][0][15]
		jWW 			= json_obj['obs'][0][3]

		AlertList	= [jWW,jRW,jWC,jBV,jHH,jHH,jRA,jHU,jUV]	

		for a, b, c, d, e, f in zip(AlertList, MsgList, Warning, Thresholds, Operator, NumonicList):
			msg = getAlert(a, d, c, b, f, e)


		#Now lets loop through the list and see what alerts we need to send.
		#We have a warning
		if len(msg) > 0:
			#First, lets check if the message has already been sent
			messageSent = msg[-1]
			if messageSent > 1:
				print('message is already sent')
			else:
				print('send the alert')
				SendNotification(listToString(msg[1]))
	except:
		pass
	
while True:
	opensocket()
	print('sleeping')
	time.sleep(10)
	
