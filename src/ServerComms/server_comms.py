# -*- coding: utf-8 -*-
import datetime
from cgi import parse_qs, escape
from wsgiref.simple_server import make_server
import httplib, urllib
import sys
import json
import os
import requests
from datetime import datetime as dt
import time
from pprint import pprint as pp
import shutil
import binascii
import threading
import schedule
import socket

#globals: read from cinfig file
port = 0
ip = ''
images_dir = ''
clone_dir = ''
pi_id = 0
store_id = 0
poll_sleep_time = 0 #in seconds
heartbeat_sleep_time = 0
log_file = ''
image_server_url = ''
otp = 0
email = ''
raw_url = ''


def read_config_file():
	global log_file, ip, port, images_dir, poll_sleep_time, clone_dir, pi_id, store_id, url, heartbeat_sleep_time, email
	
	client_config_file = 'client_config.json'
	f = open(client_config_file)
	for line in f:
		line = line.strip()
		if line != '':
			try:
				t = json.loads(line.strip())
				print
			except Exception as e:
				print 'Error loading config json',e
				return False
	f.close()
	
	port = int(t.get('port',-1))
	ip = str(t.get('ip', 0))
	email = t.get('email','')
	#images_dir = t.get('images_dir',None)
	
	#poll_sleep_time = t.get('poll_sleep_time',-1)
	#clone_dir = t.get('clone_dir',None)
	#heartbeat_sleep_time = t.get('heartbeat_sleep_time',-1)
	#url = t.get('url',0)
	#log_file = t.get('log_file','')
	
	#if url == 0 or (not images_dir)or poll_sleep_time == -1 or (not clone_dir) or log_file == '' or heartbeat_sleep_time == -1:
	if email == '':
		print 'Invalid/Absent values in config file'
		return False
	return True


def get_otp_url(raw_url, info_dict):
	print 'Info',info_dict
	#http://ubu2.westcentralus.cloudapp.azure.com:7009/iot/api/pi/heartbeat?ip=192.176.12.12&datetime=2018-01-08%2012%3A00%3A34&emailId=mukesh%40sumyag.com
	try:
		#raw_url = 'http://ubu2.westcentralus.cloudapp.azure.com:7009/iot/api/pi/sendConfigFile'
		tail = urllib.urlencode(info_dict)
		res = requests.get(raw_url+tail)
		print res.status_code
	except Exception as e:
		print 'Exception in initial post request-get_otp_url',e
		sys.exit()

	return res.text


def get_init_info():
	global email

	ip = socket.gethostbyname(socket.gethostname())
	date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	info_dict = dict(ip='%s' %ip, datetime='%s' %date, emailId ='%s' %email)

	return info_dict


def main(argv):
	global raw_url
	import webbrowser
	
	raw_url = 'http://ubu2.westcentralus.cloudapp.azure.com:7009/iot/api/pi/heartbeat?'
	global port, ip, image_server_url, otp
	is_config = read_config_file()
	if not is_config:
		sys.exit('Absent/invalid values in config file')

	info_dict = get_init_info()
	init_response = get_otp_url(raw_url,info_dict)
	print init_response
	print 

	with open('first_response.json','wb') as f:
		f.write(init_response)
	f.close()

	init_response_dict = json.loads(init_response)
	print init_response_dict
	url_to_open_in_web = init_response_dict.get('url','')
	new_otp = init_response_dict.get('otp','')
	email = init_response_dict.get('emailId','')
	webbrowser.open(url_to_open_in_web, new=1)
	
	raw_input()

	temp_dict = dict(otp='%s' %new_otp)
	second_response = get_otp_url('http://ubu2.westcentralus.cloudapp.azure.com:7009/iot/api/pi/sendConfigFIle?',temp_dict)
	print second_response

	with open('second_response.json','wb') as f:
		f.write(second_response)
	f.close()


if __name__ == "__main__":
	main(sys.argv)
