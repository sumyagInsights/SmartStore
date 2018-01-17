import datetime
import sys
import json
import os
import requests
import hashlib


def heartbeat_ping(url):
	try:
		ping_response = requests.get(url)
	except Exception as e:
		print 'Exception in heartbeat ping',e
		return 
	return ping_response.text


def main():
	url = 'http://ubu2.westcentralus.cloudapp.azure.com:7009/iot/api/pi/'#set server url here
	uri_response = heartbeat_ping(url)
	uri_responce_dict = json.loads(uri_response)
	#print uri_responce_dict
	
	#uri_responce_dict = {"otp":1234,"contentUrl":[('abc','123'),('def','456'),('ghi','789')],"content_type":"jpeg"}
	
	uri_list = uri_responce_dict.get('contentUrl',[])
	content_type = uri_responce_dict.get('content_type','')
	#print uri_list
	
	#set local directory where files will be saved.
	file_dir = ''
	if len(uri_list) == 0:
		print 'No URIs in ping responce'
	else:
		response_list = []
		for tupple in uri_list:
			res = requests.get(tupple[0])
			
			if tupple[1] == hashlib.md5(res.content).hexdigest():#if checksum matches then save file & respond with 'ACK' else respond with 'NAK'
				responce = 'ACK'
				with open(str(file_dir+time.time())+'.'+content_type,'wb') as f:#save file with timestamp as name
					f.write(res.content)
					f.close()
			else:
				response = 'NAK'
			response_list.append((tupple[0],response))
		
	r = requests.post(url, data = dict(response=response_list))#send ACK/NAK for each URIs back to server


if __name__ == "__main__":
	main(sys.argv)
