from websocket import create_connection
from urllib.request import urlopen
import json
from datetime import datetime
import requests as req
import http.client, urllib
import time

personal_token = "[personal token]"
tempest_ID = '[tempist ID]'
station_id = "[station ID]"
push_token = "[Push Token]"
user = "[user id]"

def SendNotification(Title):
	r = req.post("https://api.pushover.net/1/messages.json", data = {
	"token": push_token,
	"user": user,
	"message": "Weather Warning: " + '\n' + Title
	},
	files = {
		"attachment": ("warning.jpg", open(r"d:\python\weather\warning.jpg", "rb"), "image/jpeg")
	})

def opensocket():
	websock = create_connection('wss://ws.weatherflow.com/swd/data?api_key=' + personal_token)
	temp_rs =  websock.recv()
	websock.send('{"type":"listen_start",'       + ' "device_id":' + tempest_ID + ',' + ' "id":"Tempest"}')
	temp_rs =  websock.recv()
	temp_rs =  websock.recv()
	websock.close()

	""" 
  UV Index rules
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
	a_wind_warning 		  = 15	#Alert if we get wind more than 15kms
	a_rain_warning 		  = 5		#Alert if we get 5mm or more of rain
	a_heat_index_high 	= 30	#Alert if the temp gets above 30	
	a_heat_index_low 	  = 5		#Alert if the temp gets above 30	
	a_strike_count 		  = 5		#Alert if we get more than 5 lightning strikes in the last hour
	a_wind_chill 		    = 5		#Alert if the windchill is 5 or lower
	a_battery 			    = 2		#Alert if battery level drops
	a_uv 				        = 6		#UV index alert
	a_radiation 		    = 1380	#This is a normal value
	a_humidity_high 	  = 98	#High and low values for humidity
	a_humidity_low 		  = 20	#Low humidity values

	#Define what we want to check
	WW = 'Wind Warning:'
	RW = 'Rain Warning:'
	WC = 'Wind Chill Warning:'
	BV = 'Battery Voltage Warning:'
	HH = 'High Heat Warning:'
	CW = 'Cold Warning:'
	RA = 'Radiation Warning:'
	HU = 'High Humidity Warning:'
	HL = 'Low Humidity Warning:'

	#Read the json into variables
	json_obj 		    = json.loads(temp_rs)
	rain_lasthour 	= json_obj['summary']['precip_total_1h']
	wind_chill 		  = json_obj['summary']['wind_chill']
	feels_like 		  = json_obj['summary']['feels_like']
	heat_index 		  = json_obj['summary']['heat_index']
	battery 		    = json_obj['obs'][0][16]
	uv_index 		    = json_obj['obs'][0][10]
	humidity 		    = json_obj['obs'][0][8]
	rain_for_today 	= json_obj['obs'][0][18]
	lux 			      = json_obj['obs'][0][9]
	radiation 		  = json_obj['obs'][0][11] 
	gust 			      = json_obj['obs'][0][3]
	strike_count 	  = json_obj['obs'][0][15]

	#print out any of the results
	print('Rain Last Hour:', rain_lasthour)
	print('Wind Chill:', wind_chill)
	print('Heat Index:', heat_index)
	print('Feels Like:', feels_like)
	print('Battery:', battery,  'volts')
	print('UV index:', uv_index)
	print('Humidity:', humidity, "%")
	print('Lighting (last hour):', strike_count)
	print('LUX:', lux)
	print('Rain for Today:', rain_for_today)
	print('Solar Radiation:', radiation,'(W/m^2)')
	print('--------------------------------------')
	print('Start Alerts')



	#We need to ensure we are not sending the same warning over and over, once it's below the threshold we can reset the value

	#Lets open the last file and see what we have
	with open('lastrun.txt') as f:
		filecontents = f.read().splitlines()	
		
	lastrun 	= open("lastrun.txt", "w")

	if gust >= a_wind_warning and filecontents in WW:
		msg0 	= WW + str(gust) + "kmh" +	'\n'
		lastrun.write(WW)
	if rain_lasthour >= a_rain_warning and filecontents in RW:
		msg1 	= 	WW + str(rain_lasthour) + "mm" + '\n'
		lastrun.write(RW)
	if wind_chill <= a_wind_chill:
		msg2 	= WC + str(rain_lasthour) + '\n'
	if battery <= a_battery:
		msg3 	=	BV + str(battery) + "volts" +'\n'
	if heat_index >= a_heat_index_high:
		msg4 	=  HH +  str(heat_index)+ "C" + '\n'
		lastrun.write(HH)
	if heat_index <= a_heat_index_low:
		msg5 	= CW + str(heat_index) + "C" + '\n'
		lastrun.write(CW)
	if radiation >= a_radiation:
		msg6 	= RA + str(radiation)+ '\n'
		lastrun.write(RA)
	if humidity >= a_humidity_high and str(filecontents) in HU:
		msg7 	= HU + str(humidity) +"%" + '\n'
		lastrun.write(HU)
	if humidity <= a_humidity_low and filecontents in HL:
		msg8 	= HL + str(humidity) + "%" + '\n'
		lastrun.write(HL)
	lastrun.close()

	warnings	= f"{msg0}{msg1}{msg2}{msg3}{msg4}{msg5}{msg6}{msg7}"

	if len(warnings) > 0:
		#print(warnings)
		SendNotification(warnings)
	else:
		print('No warnings')
		
while True:
	opensocket()
	print('sleeping')
	time.sleep(60) #Sleep for 60 seconds
	
