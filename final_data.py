import xml.etree.ElementTree as ET
import urllib.request
import json
import redis
import copy
import itertools

r = redis.Redis(host='localhost', port=6379, db=0)

def extract_sum(combos, user_input):
	for v in combos:
		sum1 = 0
		for s in v:
			if type(s) == str:
				if "p" in s:
					sum1 += int(s.split("p")[0])
				else:
					sum1 += int(s.split("n")[0])
			elif type(s) == int:
				sum1 += s
		print(sum1)
		if sum1 == user_input:
			return v, sum1


def find_match_ads(pre_durations, non_durations, user_input):
	search_ads_data = []
	pre_combos = set([combo for length in range(1, len(pre_durations)) for combo in itertools.combinations(pre_durations, length)])
	# non_combos = set([combo for length in range(1, len(non_durations)) for combo in itertools.combinations(non_durations, length)])

	comb, sum = extract_sum(pre_combos, user_input)

	for f in comb:
		if type(f) == int:
			found_index = pre_durations.index(f)
			search_ads_data.append(found_index) #ads
		elif type(f) == str:
			if "p" in f:
				val = int(f.split("p")[1])
			else:
				val = int(f.split("n")[1])
			search_ads_data.append(val) #ads
	return search_ads_data

def parse_xml(dur_second):
	tree = ET.parse('vast.xml')
	root = tree.getroot()
	Ad_sequence, AdID, AdTitle, Description, Error, Impression, Creatives, creative_id, creative_sequence, ad_type, Duration, TrackingEvents, start, firstQuartile, midpoint, thirdQuartile, complete, mute, unmute, rewind, pause, resume, creativeView, fullscreen, acceptInvitationLinear, closeLinear, exitFullscreen, ClickThrough_id, ClickThrough_text, media_type, id, media_delivery, media_width, media_height, media_Aspectratio, media_sclable, media_bitrate, media_source = "","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""
	final_dic = {}

	ads = []
	ads_dic = {}
	ads_data = {}
	crs = []
	crs_dict = {}
	events = []
	TrackEvents = []
	TrackingEvents = {}
	events_dict = {}

	duration_count = 0
	pre_transcoded = []
	non_transcoded = []

	for ad in root.findall("./Ad"):
		Ad_sequence = ad.attrib["sequence"]
		AdID = ad.attrib["id"]
		ads_dic["Ad_sequence"] = Ad_sequence
		ads_dic["AdID"] = AdID
		for node in ad.iter():
			if node.tag =='AdTitle':
				AdTitle = node.text
				ads_dic["AdTitle"] = AdTitle
			if node.tag =='Description':
				Description = node.text
				ads_dic["Description"] = Description
			if node.tag =='Error':
				Error = node.text
				ads_dic["Error"] = Error
			if node.tag =='Impression':
				Impression = node.text
				ads_dic["Impression"] = Impression
		for cr in ad.findall("./InLine/Creatives/Creative"):
			creative_sequence = ad.attrib["sequence"]
			creative_ID = ad.attrib["id"]

			crs_dict["creative_ID"] = creative_ID # if id present in redis key then add in pre_transcoded_list AND if not satisfied then add n non_transcoded
			crs_dict["creative_sequence"] = creative_sequence
			for cr_node in cr.iter():
				if cr_node.tag =='UniversalAdId':
					ad_type = cr_node.text
					crs_dict["type"] = ad_type
				if cr_node.tag =='Duration':
					duration = sum(x * int(t) for x, t in zip([3600, 60, 1], cr_node.text.split(":")))
					crs_dict["Duration"] = duration
				
					check_key = "creative_"+creative_ID
					check = r.get(check_key)
					c_d = {}
					c_d["duration"] = duration
					c_d["creative_ID"] = creative_ID
					if check:
						pre_transcoded.append(c_d) # [{"duration": 20,"creative_ID":12323},...]
					else:
						non_transcoded.append(c_d)
					
					print("pre with creatives..",pre_transcoded)
					print("non with creatives",pre_transcoded)

				# TrackingEvents Started
				if cr_node.tag =='Tracking':
					if cr_node.attrib["event"] == "start":
						start = cr_node.text
						events_dict["start"] = start
					if cr_node.attrib["event"] == "firstQuartile":
						firstQuartile = cr_node.text
						events_dict["firstQuartile"] = firstQuartile
					if cr_node.attrib["event"] == "midpoint":
						midpoint = cr_node.text
						events_dict["midpoint"] = midpoint
					if cr_node.attrib["event"] == "thirdQuartile":
						thirdQuartile = cr_node.text
						events_dict["thirdQuartile"] = thirdQuartile
					if cr_node.attrib["event"] == "complete":
						complete = cr_node.text
						events_dict["complete"] = complete
					if cr_node.attrib["event"] == "mute":
						mute = cr_node.text
						events_dict["mute"] = mute
					if cr_node.attrib["event"] == "unmute":
						unmute = cr_node.text
						events_dict["unmute"] = unmute
					if cr_node.attrib["event"] == "rewind":
						rewind = cr_node.text
						events_dict["rewind"] = rewind
					if cr_node.attrib["event"] == "pause":
						pause = cr_node.text
						events_dict["pause"] = pause
					if cr_node.attrib["event"] == "resume":
						resume = cr_node.text
						events_dict["resume"] = resume
					if cr_node.attrib["event"] == "creativeView":
						creativeView = cr_node.text
						events_dict["creativeView"] = creativeView
					if cr_node.attrib["event"] == "creativeView":
						creativeView = cr_node.text
						events_dict["creativeView"] = creativeView
					if cr_node.attrib["event"] == "fullscreen":
						fullscreen = cr_node.text
						events_dict["fullscreen"] = fullscreen
					if cr_node.attrib["event"] == "acceptInvitationLinear":
						acceptInvitationLinear = cr_node.text
						events_dict["acceptInvitationLinear"] = acceptInvitationLinear
					if cr_node.attrib["event"] == "closeLinear":
						closeLinear = cr_node.text
						events_dict["closeLinear"] = closeLinear
					if cr_node.attrib["event"] == "exitFullscreen":
						exitFullscreen = cr_node.text
						events_dict["exitFullscreen"] = exitFullscreen
					TrackEvents.append(events_dict)
				TrackingEvents["TrackingEvents"] = TrackEvents
				# TrackingEvents Ended

				if cr_node.tag =='ClickThrough':
					ClickThrough_id = cr_node.attrib["id"]
					ClickThrough_text = cr_node.text
					crs_dict["ClickThrough_id"] = ClickThrough_id
					crs_dict["ClickThrough_text"] = ClickThrough_text
				
				# MediaFile Started
				for mf in cr_node.findall("./MediaFile"):
					media_type = mf.attrib["type"] or ""
					crs_dict["media_type"] = media_type
					id = mf.attrib["id"] or ""
					crs_dict["id"] = id
					media_delivery = mf.attrib["delivery"] or ""
					crs_dict["media_delivery"] = media_delivery
					media_width = mf.attrib["width"] or ""
					crs_dict["media_width"] = media_width
					media_height = mf.attrib["height"] or ""
					crs_dict["media_height"] = media_height
					media_Aspectratio = mf.attrib["maintainAspectRatio"] or ""
					crs_dict["media_Aspectratio"] = media_Aspectratio
					media_sclable = mf.attrib["scalable"] or ""
					crs_dict["media_sclable"] = media_sclable
					if mf.attrib == "bitrate":
						media_bitrate = mf.attrib["bitrate"]
						crs_dict["media_bitrate"] = media_bitrate
					media_source = mf.text or ""
					# MediaFile Started

					crs_dict["media_source"] = media_source
					crs_dict["TrackingEvents"] = TrackEvents
			ads.append(ads_dic)
			ads.append(crs_dict)
		ads_data["ads"] = ads

	pre_dur = []
	non_dur = []
	for pt in pre_transcoded:
		pre_dur.append(pt["duration"])
		
	for nt in non_transcoded:
		non_dur.append(nt["duration"])

	# Final list to process
	print("pre..",pre_dur)
	print("non..",non_dur)

	pre_dur_copy = copy.deepcopy(pre_dur)
	non_dur_copy = copy.deepcopy(non_dur)

	pre_durations = [str(str(ele)+"p"+str(idx)) if (ele in pre_dur_copy[ :idx]) else ele for idx, ele in enumerate(pre_dur_copy)]
	non_durations = [str(str(ele)+"n"+str(idx)) if (ele in non_dur_copy[ :idx]) else ele for idx, ele in enumerate(non_dur_copy)]
	
	

	search_ads_data = ""
	# search_ads_data = find_match_ads(pre_durations,dur_second)
	search_ads_data = find_match_ads(pre_durations,non_durations,dur_second)
	# search_ads_data = find_match_ads(non_durations,dur_second)

subarray whos sum is 
	print(search_ads_data)

	final_creatives = []
	for fc in search_ads_data:
		final_creatives.append(pre_transcoded[fc])
	print("pre...: ",final_creatives)

user_input = int(input("Enter ads duration: "))
parse_xml(user_input)