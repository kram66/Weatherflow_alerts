from websocket import create_connection
from urllib.request import urlopen
import json
from datetime import datetime
import requests as req
import http.client, urllib
import time



personal_token = "your token here"
tempest_ID = "your tempest id here"
station_id = "your station id here"
push_token = "your push notification here"
user = "your user here"

thislist = []

def nonzero(value):
    if value == None:
        return 0
    return value

	
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

def opensocket():
	try:
		#print('Opening Websocket connection...')
		websock = create_connection('wss://ws.weatherflow.com/swd/data?api_key=' + personal_token)
		temp_rs =  websock.recv()
		websock.send('{"type":"listen_start",'       + ' "device_id":' + tempest_ID + ',' + ' "id":"Tempest"}')
		temp_rs =  websock.recv()
		#Lets process the result
		temp_rs =  websock.recv()
		#Lets close the socket
		websock.close()

		""" 
		low (1-2)
		moderate (3-5)
		high (6-7)
		very high (8-10)
		extreme (11 and above).
		"""


		#Define some variables
		msg0 	= ""
		msg1 	= ""
		msg2 	= ""
		msg3 	= ""
		msg4 	= ""
		msg5 	= ""
		msg6 	= ""
		msg7 	= ""
		msg8 	= ""


		#Lets setup some defaults for our alerts
		a_wind_warning 		= 15	#Alert if we get wind more than 15kms
		a_rain_warning 		= 5	#Alert if we get 5mm or more of rain
		a_heat_index_high 	= 30	#Alert if the temp gets above 30	
		a_heat_index_low 	= 5	#Alert if the temp gets above 30	
		a_strike_count 		= 5	#Alert if we get more than 5 lightning strikes in the last hour
		a_wind_chill 		= 5	#Alert if the windchill is 5 or lower
		a_battery 		= 2	#Alert if battery level drops
		a_uv 			= 6	#UV index alert
		a_radiation 		= 1380	#This is a normal value
		a_humidity_high 	= 95	#High and low values for humidity
		a_humidity_low 		= 20	#Low humidity values

		#Define what we want to check
		WW = 'Wind Warning: '
		RW = 'Rain Warning: '
		WC = 'Wind Chill Warning: '
		BV = 'Battery Voltage Warning: '
		HH = 'High Heat Warning: '
		CW = 'Cold Warning: '
		RA = 'Radiation Warning: '
		HU = 'High Humidity Warning: '
		HL = 'Low Humidity Warning: '

		#Read the json into variables
		json_obj 		= json.loads(temp_rs)
		rain_lasthour 		= json_obj['summary']['precip_total_1h']
		wind_chill 		= json_obj['summary']['wind_chill']
		feels_like 		= json_obj['summary']['feels_like']
		heat_index 		= json_obj['summary']['heat_index']
		battery 		= json_obj['obs'][0][16]
		uv_index 		= json_obj['obs'][0][10]
		humidity 		= nonzero(json_obj['obs'][0][8])
		rain_for_today 		= json_obj['obs'][0][18]
		lux 			= nonzero(json_obj['obs'][0][9])
		radiation 		= nonzero(json_obj['obs'][0][11])
		gust 			= json_obj['obs'][0][3]
		strike_count 		= json_obj['obs'][0][15]

		#We need to ensure we are not sending the same warning over and over, once it's below the threshold we can reset the value

		if humidity >= a_humidity_high:
			newstring= "HU:" + str(humidity)
			if newstring not in thislist:
				thislist.append(newstring)
				msg0 	= HU + str(humidity) + '%' + '\n'
		elif humidity <= a_humidity_high:
			newstring= "HU:" + str(humidity)
			if newstring in thislist: thislist.remove(newstring) 
		
		if humidity <= a_humidity_low:
			newstring= "HL:" + str(humidity)
			if newstring not in thislist:
				thislist.append(newstring)
				msg1 	= HL + str(humidity) + '%' + '\n'
		elif humidity >= a_humidity_low:
			newstring= "HL:" + str(humidity)
			if newstring in thislist: thislist.remove(newstring) 
			
		if gust >= a_wind_warning:
			newstring= "WW:" + str(gust)
			if newstring not in thislist:
				thislist.append(newstring)
				msg2 	= WW + str(gust) + 'KM' + '\n'
		elif gust <= a_wind_warning:
			newstring= "WW:" + str(gust)
			if newstring in thislist: thislist.remove(newstring) 	
			
		if wind_chill <= a_wind_chill:
			newstring= "WC:" + str(wind_chill)
			if newstring not in thislist:
				thislist.append(newstring)
				msg3 	= WC + str(wind_chill) + 'C' + '\n'
		elif wind_chill >= a_wind_chill:
			newstring= "WC:" + str(wind_chill)
			if newstring in thislist: thislist.remove(newstring) 	

		if battery <= a_battery:
			newstring= "BV:" + str(battery)
			if newstring not in thislist:
				thislist.append(newstring)
				msg4 	= BV + str(battery) + 'V' + '\n'
		elif battery >= a_battery:
			newstring= "BV:" + str(battery)
			if newstring in thislist: thislist.remove(newstring) 
		
		if heat_index >= a_heat_index_high:
			newstring= "HH:" + str(heat_index)
			if newstring not in thislist:
				thislist.append(newstring)
				msg5 	= HH + str(heat_index) + 'C' + '\n'
		elif heat_index <= a_heat_index_high:
			newstring= "HH:" + str(heat_index)
			if newstring in thislist: thislist.remove(newstring) 
		
		if heat_index <= a_heat_index_low:
			newstring= "CW:" + str(heat_index)
			if newstring not in thislist:
				thislist.append(newstring)
				msg6 	= CW + str(heat_index) + 'C' + '\n'
		elif heat_index >= a_heat_index_low:
			newstring= "CW:" + str(heat_index)
			if newstring in thislist: thislist.remove(newstring) 
		
		if radiation >= a_radiation:
			newstring= "RA:" + str(radiation)
			if newstring not in thislist:
				thislist.append(newstring)
				msg7 	= RA + str(radiation) + 'W/m^2' + '\n'
		elif radiation <= a_radiation:
			newstring= "RA:" + str(radiation)
			if newstring in thislist: thislist.remove(newstring) 
			
			
		warnings = f"{msg0}{msg1}{msg2}{msg3}{msg4}{msg5}{msg6}{msg7}"
		
		print(warnings)
		if len(warnings) > 0:
			print(warnings)
			SendNotification(warnings)
			print('sending notification')
			
		else:
			print('No warnings or already sent')
	except:
		pass

	
while True:
	opensocket()
	print('sleeping')
	time.sleep(20)
	
