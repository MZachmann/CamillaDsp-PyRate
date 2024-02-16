import time
import websocket
import json

COMMENT=''' This modules is for use in conjunction with a running CamillaDsp
It checks the incoming capture data rate and puts it in one of a small set of buckets
If the bucket has changed it selects the bucket's configuration .yml file
and tells CamillaDsp to use the new configuration
'''

targets = [44100, 48000, 96000] # available capture rate buckets
filenames = ['Usb44', 'Usb48', 'Usb96'] # associated yml files
configPath = '/home/mark/camilladsp/configs/' # path for all yml files

def ToRate(whom) :
	''' Look for a rate in the list of targets
	return the rate and the desired filename if found
	else return 0
	'''
	j = 0
	for x in targets:
		if (whom * .99) < x and (whom * 1.01) > x :
			# the +-1% range found something
			return x, configPath + filenames[j] + '.yml'
		j = j + 1
	return 0,0

def NotIndex(l : list, x) :
	''' return the index of the first non-x
	'''
	n = len(l)
	for i in range(n):
		if l[i] != x:
			return i-1
	return n-1

def ListFull(srclist : list, rate) :
	''' look to see if the list is entirely 'rate'
	if so, return True
	if not, update the first not-rate value and return False
	'''
	l = srclist  # shrink
	print('check list with' + str(rate))
	if rate != 0:
		j = 1 + NotIndex(l, rate)
		if j == (len(l)):
			return True
		l[j] = rate # add it to the list
		if(j==1):
			for j in range(j+1, len(l)):
				l[j] = 0
	return False

def IsWsConnected(ws : websocket):
	bout = False
	try:
		ws.recv()
		bout = ws.connected
	except Exception as e:
		print("connect error: " + str(e))
	return bout

def DoMain() :
	''' Infinite loop of ask CamillaDsp what the capture rate is and
	if it has changed then set a new configuration file
	'''
	currentrate = 0
	while 1:
		fndlist = [0,0,0] # lets ensure we get the same value 3 times
		try:
			ws = websocket.create_connection("ws://127.0.0.1:1234")
			while 1:
				# only proceed if CamillaDsp state is running
				ws.send(json.dumps('GetState'))
				u = ws.recv() # read the current state and check for Running
				if not 'Running' in u :
					fndlist = [0,0,0]
					continue
				# get the (float) capture rate and see if it's one we expect
				try:
					ws.send(json.dumps('GetCaptureRate'))
				except Exception as e:
					print('Exception0 ' + str(e))
					continue # ignore random fail?
				rate = json.loads(ws.recv())
				# print("rate={0}".format(rate))
				nowrate = rate["GetCaptureRate"]["value"]
				# which predefined rate is it?
				found,newsample = ToRate(nowrate)

				if (found == 0) :
					found = -1
				# print("Rate found={0} at {1}".format(found, newsample))
				if (found != currentrate) :
					# print("found is {0} rate is {1}".format(found,currentrate))
					listfull = ListFull(fndlist, found)
					if listfull:
							# print("Switching to " + newsample)
							# do rate change
							try:
								# multiple failures, retry with 96K
								if (found == -1) :
									found,newsample = ToRate(96000)
								# if 'RUNNING' read the yml file
								with open(newsample) as f:
									cfg = f.read()
								# remove everything after the device settings
								f = cfg.find('filter:') # remove excess stuff
								if ( f>0) :
									cfg = cfg[:f]
								# send the device settings to CamillaDsp
								ws.send(json.dumps({"SetConfig": cfg}))
								# print("reset name to:{0}".format(newsample)) # status
								ws = websocket.create_connection("ws://127.0.0.1:1234") # renew this?
								currentrate = found
								fndlist = [0,0,0]
							except Exception as e:
								print('Exception ' + str(e))
								pass
					else:
						# ws.send(json.dumps("GetConfigName"))
						# u = ws.recv() # for diagnostic here
						# print("config={0}".format(json.loads(u)))
						# print("list is {0}".format(fndlist))
						pass
					time.sleep(.3) # the rate hasn't stabilized, check more often
				else:
					time.sleep(1) # the rate is still what it was, sleep a bit
		except Exception as e:
			print('Exception2 ' + str(e))
			time.sleep(0.1) # we can't go into a cpu-kill loop
			pass

# run the main app
DoMain()
