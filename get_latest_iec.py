import json
import os
import sys
from glob import *
from api.models import *
from api import db
import urllib2
from time import strptime

party_name_overrides = {
	"DEMOCRATIC ALLIANCE/DEMOKRATIESE ALLIANSIE": "DEMOCRATIC ALLIANCE",
	"CONGRESS  OF THE PEOPLE": "CONGRESS OF THE PEOPLE",
	"VRYHEIDSFRONT \\ FREEDOM FRONT": "FREEDOM FRONT",
	"CAPE PARTY/ KAAPSE PARTY": "CAPE PARTY",
}

province_keys = {
	"LIMPOPO": "LIM",
	"MPUMALANGA": "MP",
	"NORTH WEST": "NW",
	"GAUTENG": "GT",
	"KWAZULU-NATAL": "KZN",
	"EASTERN CAPE": "EC",
	"FREE STATE": "FS",
	"NORTHERN CAPE": "NC",
	"WESTERN CAPE": "WC",
}

province_order = { "EC": 1, "FS": 2, "GT": 3, "KZN": 4, "MP": 5, "NC": 6, "LIM": 7, "NW": 8, "WC": 9 }

def download_latest_results(id):
	ward_queue = []
	municipality_queue = []
	province_queue = []
	jdata = urllib2.urlopen("http://localhost:8082/latest/" + str(id)).read()
	data = json.loads(jdata)
	for item in data:
		try:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S.%f')
		except:
			dt = strptime(item["ReleasedDate"], '%Y-%m-%dT%H:%M:%S')
		query = db.session.query(VotingDistrict).filter(VotingDistrict.year == int(dt.tm_year), VotingDistrict.voting_district_id == int(item["VDNumber"]))
		check_result = query.first()
		check_field_national = json.loads(check_result.results_national)
		check_field_provincial = json.loads(check_result.results_provincial)
		if (int(check_field_national["meta"]["vote_complete"]) + int(check_field_provincial["meta"]["vote_complete"]) < 200):
			uri = "http://localhost:8082/result/" + str(id) + "/voting_district/"+ str(item["VDNumber"])
			print uri
			jvddata = urllib2.urlopen(uri).read()
			vddata = json.loads(jvddata)
			if int(id) == int(vddata["ElectoralEventID"]):
				print "Looks valid for " + str(vddata["ElectoralEvent"])
				data_dict = {'meta': {}, 'vote_count': {}}
				data_dict["meta"]["num_registered"] = vddata['RegisteredVoters']
				data_dict["meta"]["turnout_percentage"] = vddata['PercVoterTurnout']
				data_dict["meta"]["vote_count"] = vddata['TotalValidVotes']
				data_dict["meta"]["spoilt_votes"] = vddata['SpoiltVotes']
				data_dict["meta"]["total_votes"] = vddata['TotalVotesCast']
				data_dict["meta"]["section_24a_votes"] = vddata['Section24AVotes']
				data_dict["meta"]["special_votes"] = vddata['SpecialVotes']
				if (vddata['bResultsComplete']):
					data_dict["meta"]["vote_complete"] = 100
				else:
					data_dict["meta"]["vote_complete"] = round(float(vddata['VDWithResultsCaptured']) / float(vddata['VDCount']) * 100, 2)
				for party_data in vddata["PartyBallotResults"]:
					data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
				if (str(vddata["ElectoralEvent"]).lower().find("national") > -1):
					check_field = check_field_national
				else:
					check_field = check_field_provincial
				if int(check_field["meta"]["vote_complete"]) < 100:
					print "Updating this one"
					if (str(vddata["ElectoralEvent"]).lower().find("national") > -1):
						query.update({ 'results_national': json.dumps(data_dict) })
					else:
						query.update({ 'results_provincial': json.dumps(data_dict) })
					db.session.commit()
					ward_queue.append(check_result.ward_pk)
					municipality_queue.append(check_result.municipality_pk)
					province_queue.append(check_result.province_pk)
				else:
					print str(vddata["ElectoralEvent"]).lower().find("national"), int(check_field["meta"]["vote_complete"]), int(check_field["meta"]["total_votes"]), check_result.pk
	calculate_ward(set(ward_queue), dt.tm_year)
	calculate_municipality(set(municipality_queue), dt.tm_year, id)
	calculate_province(set(province_queue), dt.tm_year, id)
	calculate_national(dt.tm_year, id)

def calculate_ward(ward_queue, year):
	for ward_pk in ward_queue:
		query = db.session.query(VotingDistrict).filter(VotingDistrict.year == int(year), VotingDistrict.ward_pk == int(ward_pk))
		vds = query.all()
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = 0
		data_dict["meta"]["turnout_percentage"] = 0
		data_dict["meta"]["vote_count"] = 0
		data_dict["meta"]["spoilt_votes"] = 0
		data_dict["meta"]["total_votes"] = 0
		data_dict["meta"]["section_24a_votes"] = 0
		data_dict["meta"]["special_votes"] = 0
		data_dict["meta"]["vote_complete"] = 0
		data_dict_national = data_dict_provincial = data_dict
		count = 0;
		for vd in vds:
			data_national = json.loads(vd.results_national)
			data_provincial = json.loads(vd.results_provincial)
			for key in data_national["meta"]:

				data_dict_national["meta"][key] = int(data_dict_national["meta"].get(key, 0)) + int(data_national["meta"][key])
			for key in data_provincial["meta"]:
				data_dict_provincial["meta"][key] = int(data_dict_provincial["meta"].get(key, 0)) + int(data_provincial["meta"][key])
			for key in data_national["vote_count"]:
				data_dict_national["vote_count"][key] = int(data_dict_national["vote_count"].get(key, 0)) + int(data_national["vote_count"][key])
			for key in data_provincial["vote_count"]:
				data_dict_provincial["vote_count"][key] = int(data_dict_provincial["vote_count"].get(key, 0)) + int(data_provincial["vote_count"][key])
			count = count + 1
		data_dict_national["meta"]["vote_complete"] = round(float(data_dict_national["meta"]["vote_complete"]) / float(count) * 100, 2)
		data_dict_provincial["meta"]["vote_complete"] = round(float(data_dict_provincial["meta"]["vote_complete"]) / float(count) * 100, 2)
		db.session.query(Ward).filter(Ward.pk == ward_pk).update({ 'results_national': json.dumps(data_dict_national) })
		db.session.query(Ward).filter(Ward.pk == ward_pk).update({ 'results_provincial': json.dumps(data_dict_provincial) })
		db.session.commit()

def calculate_municipality(queue, year, id):
	for pk in queue:
		query = db.session.query(Municipality).filter(Municipality.pk == pk)
		municipality = query.first()
		uri = "http://localhost:8082/result/" + str(id) + "/municipality/"+ str(municipality.municipality_id)
		print uri
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()

def calculate_province(queue, year, id):
	for pk in queue:
		query = db.session.query(Province).filter(Province.pk == pk)
		province = query.first()
		uri = "http://localhost:8082/result/" + str(id) + "/province/"+ str(province_order[province.province_id])
		print uri
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()

def calculate_national(year, id):
	uri = "http://localhost:8082/result/" + str(id)
	print uri
	query = db.session.query(Country).filter(Country.year == year)
	check_result = query.first()
	check_field_national = json.loads(check_result.results_national)
	check_field_provincial = json.loads(check_result.results_provincial)
	if (int(check_field_national["meta"]["vote_complete"]) + int(check_field_provincial["meta"]["vote_complete"]) < 200):
		print "Calculating national totals"
		jdata = urllib2.urlopen(uri).read()
		data = json.loads(jdata)
		data_dict = {'meta': {}, 'vote_count': {}}
		data_dict["meta"]["num_registered"] = data['RegisteredVoters']
		data_dict["meta"]["turnout_percentage"] = data['PercVoterTurnout']
		data_dict["meta"]["vote_count"] = data['TotalValidVotes']
		data_dict["meta"]["spoilt_votes"] = data['SpoiltVotes']
		data_dict["meta"]["total_votes"] = data['TotalVotesCast']
		data_dict["meta"]["section_24a_votes"] = data['Section24AVotes']
		data_dict["meta"]["special_votes"] = data['SpecialVotes']
		if (data['bResultsComplete']):
			data_dict["meta"]["vote_complete"] = 100
		else:
			data_dict["meta"]["vote_complete"] = round(float(data['VDWithResultsCaptured']) / float(data['VDCount']) * 100, 2)
		for party_data in data["PartyBallotResults"]:
			data_dict["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
		if (str(data["ElectoralEvent"]).lower().find("national") > -1):
			query.update({ 'results_national': json.dumps(data_dict) })
		else:
			query.update({ 'results_provincial': json.dumps(data_dict) })
		db.session.commit()


def find_latest_file():
	# print sys.argv[1]
	max_time = 0
	oldest_file = ""
	for f in glob(sys.argv[1] + "*"):
		if (max_time < os.path.getmtime(f)):
			max_time = os.path.getmtime(f)
			oldest_file = f
	f = open(oldest_file)
	return f.read()

def convert(jdata):
	data = json.loads(jdata)
	print data["ElectoralEvent"]
	data_dict = {'country': {'results': {'meta': {}, 'vote_count': {}}, 'wards': {}}}
	
	electoral_event = data['ElectoralEvent']
	# province = row.get('PROVINCE')
	# municipality = row.get('MUNICIPALITY')
	# ward = row.get('WARD')
	# voting_district = row.get('VOTING DISTRICT')
	# party_name = row.get('PARTY NAME')
	# data_dict["meta"]["num_registered"] = data['RegisteredVoters']
	# data_dict["country"]["results"]["meta"]["turnout_percentage"] = data['PercVoterTurnout']
	# data_dict["country"]["results"]["meta"]["vote_count"] = data['TotalValidVotes']
	# data_dict["country"]["results"]["meta"]["spoilt_votes"] = data['SpoiltVotes']
	# data_dict["country"]["results"]["meta"]["total_votes"] = data['TotalVotesCast']
	# data_dict["country"]["results"]["meta"]["section_24a_votes"] = data['Section24AVotes']
	# data_dict["country"]["results"]["meta"]["special_votes"] = data['SpecialVotes']
	# if (data['bResultsComplete']):
	# 	data_dict["country"]["results"]["meta"]["vote_complete"] = 100
	# else:
	# 	data_dict["country"]["results"]["meta"]["vote_complete"] = round(data['VDWithResultsCaptured'] / data['VDCount'] * 100, 2)
	# for party_data in data["PartyBallotResults"]:
	# 	data_dict["country"]["results"]["vote_count"][party_data["Name"]] = party_data["ValidVotes"]
	# 	# print party_data
	# print data_dict
	# tmp = Country(
 #        year=2014,
 #        results_national=json.dumps(data_dict["country"]['results']),
 #        results_provincial=json.dumps(data_dict["country"]['results']),
 #    )
	# db.session.add(tmp)
	if (electoral_event.lower().find("national") > -1):
		db.session.query(Country).filter(Country.year == "2014").update({ 'results_national': json.dumps(data_dict["country"]['results']) })
	else:
		db.session.query(Country).filter(Country.year == "2014").update({ 'results_provincial': json.dumps(data_dict["country"]['results']) })

def test(vd):
	data_dict = {'meta': {}, 'vote_count': {}}
	data_dict["meta"]["num_registered"] = 0
	data_dict["meta"]["turnout_percentage"] = 0
	data_dict["meta"]["vote_count"] = 0
	data_dict["meta"]["spoilt_votes"] = 0
	data_dict["meta"]["total_votes"] = 0
	data_dict["meta"]["section_24a_votes"] = 0
	data_dict["meta"]["special_votes"] = 0
	data_dict["meta"]["vote_complete"] = 0
	db.session.query(VotingDistrict).filter(VotingDistrict.voting_district_id == vd).update({ 'results_national': json.dumps(data_dict) })
	db.session.commit()

if __name__ == "__main__":
	# Find latest file
	# data = find_latest_file()
	# Convert
	# convert(data)
	# Put in DB
	# db.session.commit()
	download_latest_results(291)
	calculate_province
	# download_latest_results(292)
	# test(32862595)
	# download_latest_results(146)
	# calculate_national(2014, 291)