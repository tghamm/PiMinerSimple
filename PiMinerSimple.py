import socket
import json

import sys, subprocess, time, urllib2, socket
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from CgminerAPI import CgminerAPI

HOLD_TIME	= 3.0 #Time (seconds) to hold select button for shut down
REFRESH_TIME= 3.0 #Time (seconds) between data updates
HALT_ON_EXIT= False
lcd			= Adafruit_CharLCDPlate()
prevCol		= -1
prev		= -1
lastTime	= time.time()



def shutdown():
	lcd.clear()
	lcd.backlight(lcd.OFF)
	exit(0)

def abbrev(v):
		v = int(v)
		if v >= 1000:
			va = float(v) / 1000.0
			vs = '%.1f' % va
			vs = vs + 'k'
			return vs
		elif v >= 1000000:
			va = float(v) / 1000000.0
			vs = '%.1f' % va
			vs = vs + 'm'
			return vs
		#billion
		else:
			return '%d' % v

def hashrate(h):
	  u = 'Gh/s'
	  if h >= 1000.0:
	      u = 'Th/s'
	      h = h / 1000.0
	  elif h >= 1000000.0:
	      u = 'Th/s'
	      h = h / 1000000.0
	  s = '%s %s' % (h, u)
	  return s

def displaysimplesummary():
		lcd.clear()
		try:
			cgminer = CgminerAPI()
			summarydata = cgminer.command('summary')
			summary =  summarydata.get("SUMMARY",{})[0]
			acc = abbrev(summary.get("Accepted",{}))
			rej = abbrev(summary.get("Rejected",{}))
			hw = abbrev(summary.get("Hardware Errors",{}))
			s1 = 'A:%s R:%s H:%s' % (acc, rej, hw)
			s2 = 'avg:%s' % hashrate(float(summary.get("GHS av",{})))
			lcd.clear()
			lcd.message(s1  + '\n' + s2)
		except Exception as e:
			lcd.clear()
			print e
			lcd.message("Waiting for"  + '\n' + "cgminer ")


#Check for network connection at startup
t = time.time()
while True:
	lcd.clear()
	lcd.message('checking network\nconnection ...')
	if (time.time() - t) > 120:
		# No connection reached after 2 minutes
		lcd.clear()
		lcd.message('network is\nunavailable')
		time.sleep(30)
		exit(0)
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 0))
		lcd.backlight(lcd.ON)
		lcd.clear()
		lcd.message('IP address:\n' + s.getsockname()[0])
		time.sleep(5)
		break         		# Success
	except:
		time.sleep(1) 		# Pause a moment, keep trying
'''
	if internetOn() == True:
		time.sleep(5)
		break         # Success
	else:
		time.sleep(1) # Pause a moment, keep trying
'''


# Listen for button presses
while True:
	b = lcd.buttons()
	if b is not prev:
		if lcd.buttonPressed(lcd.SELECT):
			tt = time.time()                        # Start time of button press
			while lcd.buttonPressed(lcd.SELECT):	# Wait for button release
				if (time.time() - tt) >= HOLD_TIME: # Extended hold?
					shutdown()						# We're outta here
		#elif lcd.buttonPressed(lcd.LEFT):
		#elif lcd.buttonPressed(lcd.RIGHT):
		#elif lcd.buttonPressed(lcd.UP):
		#elif lcd.buttonPressed(lcd.DOWN):
		prev = b
		lastTime = time.time()
	else:
		now = time.time()
		since = now - lastTime
		if since > REFRESH_TIME or since < 0.0:
			#Refresh Display
			displaysimplesummary()
			lastTime = now


