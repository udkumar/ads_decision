import os
import re
import copy
import json
import logging
import requests
from flask_cors import CORS, cross_origin
from flask import Flask, request, session, redirect, jsonify, make_response
from flask_socketio import SocketIO
import pdb
import xmltodict as xtd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

import traceback
import urllib3

if 'logs' not in os.listdir(os.getcwd() + '/'):
    os.mkdir(os.getcwd() + '/logs')
logging.basicConfig(filename='logs/decision_api_logs.log', format='%(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('logs/bridge_api_logs.log')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = "decision"

CONTENT = ["https://pubads.g.doubleclick.net/gampad/ads?env=vp&gdfp_req=1&impl=s&output=vast&iu=/423477888/JIO_LiveTv_Midroll/Sony_SIX_HD_Jio_LiveTV_Midroll&sz=640x480&unviewed_position_start=1&url=http://www.sonyliv.com&correlator=0123456789&pmnd=0&pmxd=300000&pmad=10&pod=1&vpos=midroll&mridx=1&scor=17&ad_rule=0&rdid=891d5b6d-b6d8-7801-2a50-edb6db6d06dc&idtype=adid&is_lat=0&app=jio_test", "https://pubads.g.doubleclick.net/gampad/ads?env=vp&gdfp_req=1&impl=s&output=xml_vast3&iu=/423477888/Jio_TV_Plus/Jio_TV_Plus_Midroll&sz=640x480&unviewed_position_start=1&url=http://www.sonyliv.com&correlator=0123456789&pmnd=0&pmxd=60000&pmad=10&pod=1&vpos=midroll&mridx=1&scor=17&ad_rule=0&rdid=891d5b6d-b6d8-7801-2a50-edb6db6d06dc&idtype=adid&is_lat=0"]

# Read static file for code
# vast : 2 ads
# creative duration need to match with crative 
# POST method
# 

def getxml(content):
	url = content
	http = urllib3.PoolManager()
	response = http.request('GET', url)
	try:
		data = xtd.parse(response.data)
		return data
	except:
		print("Failed to parse xml from response (%s)" % traceback.format_exc())
		

@app.route('/pubads/<url>', methods=['GET']) # POST
def index(url):
	if request.method == 'GET':
		if url == "11":
			try:
				response = getxml(CONTENT[1])
				resp = jsonify({"message": response})
				return resp
			except:
				print("Failed to parse xml from response (%s)" % traceback.format_exc())

			 #render_template("index.html",data=data)
		elif url == "10":
			try:
				response = getxml(CONTENT[0])
				resp = jsonify({"message": response})
				return resp
			except:
				print("Failed to parse xml from response (%s)" % traceback.format_exc())
			


if __name__ == "__main__":
	logger.info("Starting server at http://localhost:5001")
	app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5001)