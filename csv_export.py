import json
import csv
from api.models import *
from api import db
import sys
import operator

def wards(year, ballot, lvl_id):
	rows = db.session.query(Ward).filter(Ward.year == year).all()
	results = []
	for row in rows:
		if (ballot == "national"):
			dataset = populate_dataset(json.loads(row.results_national))
		else:
			dataset = populate_dataset(json.loads(row.results_provincial))
		if (dataset):
			dataset[lvl_id] = row.as_dict()[lvl_id]
			results.append(dataset)
	return results

def populate_dataset(data):
	vote_count = sorted(data["vote_count"].iteritems(), key=operator.itemgetter(1), reverse = True)
	if (data["meta"]["vote_count"] > 0):
		result = {
			"total_votes": data["meta"]["total_votes"],
			"spoilt_votes": data["meta"]["spoilt_votes"],
			"vote_count": data["meta"]["vote_count"],
			"num_registered": data["meta"]["num_registered"],
			"winner": vote_count[0][0],
			"winner_votes": vote_count[0][1],
			"winner_perc": vote_count[0][1] / data["meta"]["vote_count"],
			"runner_up": vote_count[1][0],
			"runner_up_votes": vote_count[1][1],
			"runner_up_perc": vote_count[1][1] / data["meta"]["vote_count"],
			"difference_perc": (vote_count[0][1] - vote_count[1][1]) / data["meta"]["vote_count"]
		}
	else:
		result = False
	# print result
	return result

def print_csv(data, fname, lvl_id):
	# print data
	fieldnames = [
		lvl_id,
		"total_votes",
		"spoilt_votes",
		"vote_count",
		"num_registered",
		"winner",
		"winner_votes",
		"winner_perc",
		"runner_up",
		"runner_up_votes",
		"runner_up_perc",
		"difference_perc"
	]
	with open(fname, 'wb') as csvfile:
		csvwriter = csv.DictWriter(csvfile, fieldnames)
		csvwriter.writeheader()
		csvwriter.writerows(data)
	print "All done"

if __name__ == "__main__":
	# print len(sys.argv)
	if (len(sys.argv) == 0):
		print "Usage: python csv_export.py level national/provincial year filename"
		sys.exit(1);
	if (len(sys.argv) == 4):
		year = "2014"
	else:
		year = sys.argv[3]
	lvl = sys.argv[1]
	# print lvl
	ballot = sys.argv[2]
	fname = sys.argv[3]
	if (lvl == "wards"):
		lvl_id = "ward_id"
		data = wards(year, ballot, lvl_id)
	print_csv(data, fname, lvl_id)
	sys.exit(0)