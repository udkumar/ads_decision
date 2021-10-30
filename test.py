import traceback
import urllib3
import xmltodict

CONTENT = ["https://pubads.g.doubleclick.net/gampad/ads?env=vp&gdfp_req=1&impl=s&output=vast&iu=/423477888/JIO_LiveTv_Midroll/Sony_SIX_HD_Jio_LiveTV_Midroll&sz=640x480&unviewed_position_start=1&url=http://www.sonyliv.com&correlator=0123456789&pmnd=0&pmxd=300000&pmad=10&pod=1&vpos=midroll&mridx=1&scor=17&ad_rule=0&rdid=891d5b6d-b6d8-7801-2a50-edb6db6d06dc&idtype=adid&is_lat=0&app=jio_test", "https://pubads.g.doubleclick.net/gampad/ads?env=vp&gdfp_req=1&impl=s&output=xml_vast3&iu=/423477888/Jio_TV_Plus/Jio_TV_Plus_Midroll&sz=640x480&unviewed_position_start=1&url=http://www.sonyliv.com&correlator=0123456789&pmnd=0&pmxd=60000&pmad=10&pod=1&vpos=midroll&mridx=1&scor=17&ad_rule=0&rdid=891d5b6d-b6d8-7801-2a50-edb6db6d06dc&idtype=adid&is_lat=0"]

def getxml(content):
		url = content

		http = urllib3.PoolManager()

		response = http.request('GET', url)
		try:
				data = xmltodict.parse(response.data)
		except:
				print("Failed to parse xml from response (%s)" % traceback.format_exc())
		return data

data = getxml(CONTENT[0])
print(data)