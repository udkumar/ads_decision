import os
import glob
import xml.etree.ElementTree as ET
import urllib.request
import json
import redis
import copy
import itertools
from itertools import combinations as c
import urllib.request

r = redis.Redis(host='localhost', port=6379, db=0)

data = {'vast_urls': ['http://69.61.32.103/vast_samples/vast.xml', 'http://69.61.32.103/vast_samples/vast1.xml', 'http://69.61.32.103/vast_samples/vast2.xml', 'http://69.61.32.103/vast_samples/vast3.xml', 'http://69.61.32.103/vast_samples/vast3.xml'] }
# r.set('data', json.dumps(data))
datas = json.loads(r.get("data"))
vast_urls = datas["vast_urls"]

class AdsDecision(object):
	def __init__(self):
		self.durations = 0
		self.pre_durations = list()
		self.non_durations = list()
		self.duplicate = list()
		self.unique = list()
		self.final_index = list()
		self.pre_dur = list()
		self.non_dur = list()

	def parse_xml(self, target):
		check_duration = 0
		for file_path in vast_urls:
			with urllib.request.urlopen(file_path) as f:
				if check_duration > target:
					break

				if check_duration <= target:
					print(check_duration)
					tree = ET.parse(f)
					root = tree.getroot()

					Ad_sequence, AdID, AdTitle, Description = "","","",""
					Error, Impression, Creatives, creative_id = "","","",""
					creative_sequence, ad_type, Duration = "","",""
					TrackingEvents, start, firstQuartile = "","",""
					midpoint, thirdQuartile, complete, mute = "","","",""
					unmute, rewind, pause, resume, creativeView = "","","","",""
					fullscreen, acceptInvitationLinear, closeLinear = "","",""
					exitFullscreen, ClickThrough_id = "",""
					ClickThrough_text, media_type, mf_id, media_delivery = "","","",""
					media_width, media_height, media_Aspectratio = "","",""
					media_sclable, media_bitrate, media_source = "","",""
					
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
									check_duration += duration
									crs_dict["Duration"] = duration
									check_key = "creative_"+creative_ID
									check = r.get(check_key)
									c_d = {}
									c_d["duration"] = duration
									c_d["creative_ID"] = creative_ID
									if check:
										# print("pre...",c_d)
										pre_transcoded.append(c_d) # [{"duration": 20,"creative_ID":12323},...]
									else:
										# print("non...",c_d)
										non_transcoded.append(c_d)
									
									# print("pre with creatives..",pre_transcoded)
									# print("non with creatives",pre_transcoded)

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
									mf_id = mf.attrib["id"] or ""
									crs_dict["id"] = mf_id
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
						# print(ads_data)

					for pt in pre_transcoded:
						self.pre_dur.append(pt["duration"])
						
					for nt in non_transcoded:
						self.non_dur.append(nt["duration"])

		return self.pre_dur, self.non_dur


	# Find the closest cominations as per given input
	def find_closest(self, numbers, target):
		final_result = None
		if len(numbers) == 0:
			return False

		for combo in range(1,5):
			#lambda to find the difference between sum and target
			diff = lambda x: abs(sum(x) - target)
			#get all unique combinations
			combos = {tuple(sorted(c)) for c in c(numbers, combo)}
			#sort them
			combos = sorted(combos, key = diff)
			#get the smallest difference
			smallest = diff(combos[0])
			#filter out combos larger than the smaller difference
			result = [c for c in combos if diff(c) == smallest]

			for comb in result:
				if sum(comb) <= target:
					if smallest in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
						print('results for {}, best combinations are off by {}:'.format(target, smallest))
						final_result = comb

		return final_result

	def dup_result(self, result):
		if len(result) == 0:
			return False

		for i in result:
			if i in self.unique:
				self.duplicate.append(i)
			else:
				self.unique.append(i)
		return self.duplicate, self.unique

	def make_dup_num_dict(self, numbers):
		dict  =  {}        
		l1 = []
		for i,v in enumerate(numbers):
			if v in dict.keys():
				l1=dict[v]
				l1.append(i)
			else:
				ll=[]
				ll.append(i)
				dict[v]=ll
		return dict

	def final_outcome(self, dict, dup_result):
		for val in dup_result[1]:
			k = dict[val]
			self.final_index.append(k[0])

		if len(dup_result[0]) > 0:
			for l, m in enumerate(dup_result[0]):
				k = dict[m]
				d_len = len(dup_result[0])
				k = k[0:d_len+1]
				for t in k:
					if t not in self.final_index:
						self.final_index.append(t)
		return self.final_index


obj = AdsDecision()

target = int(input("Enter the number: "))

pre_durations, non_durations = obj.parse_xml(target)
print(pre_durations, non_durations)

pre_dict = obj.make_dup_num_dict(pre_durations)
non_dict = obj.make_dup_num_dict(non_durations)
# print(pre_num_dict, non_num_dict)

pre_non_durations = pre_durations+non_durations
# print("pre_non_durations...",pre_non_durations)
pre_non_dict = obj.make_dup_num_dict(pre_non_durations)
# print(pre_non_dict)

pre_result = obj.find_closest(pre_durations, target)
remainig = int(target - sum(pre_result))
print(remainig)


if pre_result is not None:
	if remainig > 5:
		print("mix: data...")

		non_result = obj.find_closest(non_durations, remainig)
		print(non_result)
		pre_non_element = (pre_result+non_result)
		print(pre_non_element)

		pre_non_dup_result = obj.dup_result(pre_non_element)
		final_mix_index = obj.final_outcome(pre_non_dict, pre_non_dup_result)
		print(final_mix_index)
	else:
		print("pre result...")
		print(pre_result)
		pre_dup_result = obj.dup_result(pre_result)
		final_index = obj.final_outcome(pre_dict, pre_dup_result)
		print(final_index)
else:
	print("non_result...")
	non_result = obj.find_closest(non_durations, target)
	print(non_result)
	if non_result is not None:
		non_dup_result = obj.dup_result(non_result)
		final_index = obj.final_outcome(non_dict, non_dup_result)
		print(final_index)
	else:
		final_index = "Not Found"
		print(final_index)


