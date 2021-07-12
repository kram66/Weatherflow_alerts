from websocket import create_connection
from urllib.request import urlopen
import json
from datetime import datetime
import requests as req
import http.client, urllib
import time

personal_token = "[token here]"
mytoken = "[token here]"
tempest_ID = '[token here]'
station_id = "[token here]"
push_token = "[token here]"
user = "[token here]"

"""
The UV Index divides UV radiation levels into:

low (1-2)
moderate (3-5)
high (6-7)
very high (8-10)
extreme (11 and above).
"""

		
#Lets setup some defaults for our alerts
a_WW		 		= 15	#Alert if we get wind more than 15kms
a_RW		 		= 6	#Alert if we get 5mm or more of rain
a_TH 				= 30	#Alert if the temp gets above 30	
a_TL		 		= 2 	#Alert if the temp gets below 1
a_SC		 		= 5	#Alert if we get more than 5 lightning strikes in the last hour
a_WC 				= 2	#Alert if the windchill is 5 or lower
a_BV	 			= 2 	#Alert if battery level drops
a_UV 				= 6 	#UV index alert 6 is considered high
a_RA		 		= 1380	#This is a normal value
a_HL		 		= 20	#Low humidity values

#Lists
NumonicList	= ['WW:','RW:','WC:','BV:','HH:','CW:','RA:','HL:','UV:']	
MsgList = ['Wind:','Rain:','Wind Chill:','Battery Voltage:','High Heat:','Cold:','Radiation:','Low Humidity:', 'High UV:']	
Warning = [' km',' mm',' C',' V',' C',' C',' W/m^2',' %',' I']	
Thresholds = [a_WW, a_RW, a_WC, a_BV, a_TH, a_TL, a_RA, a_HL,a_UV]
Operator = ['GT','GT','LT','LT','GT','LT','GT','LT','GT']
MyList = []


#variables
msg = ""
COUNT = 0
counter = 0
status = 'CLEAR'
interval = 10

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
	
		
def increment():
	global COUNT
	COUNT = COUNT +1
	return COUNT
	
def getAlert(AlertList, Thresholds, Warning, MsgList, NumonicList, operator):
	#Lets check if we have a warning
	MyList = [MsgList]
	if operator == "GT":
		if AlertList >= Thresholds:
			counter = increment()
			if "WARNING" not in MyList:
				MyList.append("WARNING")
				MyList.append(AlertList)
				MyList.append(Thresholds)
				MyList.append(Warning)
				MyList.append(NumonicList)
				MyList.append(counter)
				status = "WARNING"
			elif "WARNING" not in MyList and counter >1:
				MyList.pop()
				MyList.append(counter)
				status = "WARNING"
		else:
			MyList = []
			status = "CLEAR"
	else:
		if AlertList <= Thresholds:
			counter = increment()
			if "WARNING" not in MyList:
				MyList.append("WARNING")
				MyList.append(AlertList)
				MyList.append(Thresholds)
				MyList.append(Warning)
				MyList.append(NumonicList)
				MyList.append(counter)
				status = "WARNING"
			elif "WARNING" not in MyList and counter >1:
				status = "WARNING"	
				counter = increment()
				MyList.pop()
				MyList.append(counter)
		else:
			MyList = []
			status = "CLEAR"
			
	myval = "{:<19}Current: {:<12} Thresholds: {:<12} Status: {:<12}".format(MsgList, AlertList, Thresholds, status)
	print(myval)
	return MyList		
	



def opensocket():
	try:
		websock = create_connection('wss://ws.weatherflow.com/swd/data?api_key=' + personal_token)
		temp_rs =  websock.recv()
		websock.send('{"type":"listen_start",'       + ' "device_id":' + tempest_ID + ',' + ' "id":"Tempest"}')
		temp_rs =  websock.recv()

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
			if len(msg) > 0:
				msgcount = msg[-1]
				print('count=', msgcount)
				if "WARNING" in msg and msgcount == 1:
					WARNING = "WARNING"
					print('We have our first warning.. sending an alert')
					messagestring=str(msg[0]), ' ', str(msg[2]), str(msg[4]), ' - Threshold: ', str(msg[3]) 
					SendNotification(listToString(messagestring))
				elif msgcount > 1:
					print('already sent the message')
			else:
				WARNING = "CLEAR"
	except:
		pass
	
while True:
	opensocket()
	print('sleeping')
	time.sleep(interval)
