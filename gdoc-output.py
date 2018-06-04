#!/usr/bin/env python3

from datetime import date, datetime
import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name, region.name, region.country, label.abv FROM label " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "LEFT JOIN region ON winery.region = region.id " +
                        "ORDER BY winery.name, label.name, label.vintage").fetchall()

varietals = sql.execute("SELECT id, name FROM varietal ORDER BY boldness DESC").fetchall();

bottles = []
for label in labelData:
	blend = sql.execute("SELECT varietal.id, portion FROM blends " +
	                    "LEFT JOIN varietal ON blends.varietal = varietal.id " +
	                    "WHERE blends.label = ? ", (label[0],)).fetchall()

	bottleData = sql.execute("SELECT id, cost, acquisition, consumption, hold_until, boldness_coord, price_coord, hold_coord FROM bottle " +
	                         "WHERE label = ?", (label[0],)).fetchall();

	for bottle in bottleData:
		bottles.append({
			'id': bottle[0],
			'vintage': label[1],
			'winery': label[2],
			'label': label[3],
			'abv': float(label[6]),
			'cost': bottle[1],
			'acquisition': bottle[2],
			'consumed': bottle[3],
			'holdUntil': bottle[4],
			'blend': dict(blend),
			'regionDescription': label[4] + ', ' + label[5],
			'coord': (bottle[5], bottle[6], bottle[7])
		})

print("Winery,Wine Name,Year,Origin,ABV,Type,", end='')
for varietal in varietals:
	print("%s," % varietal[1], end='')

print("Unknown Blend,Unknown,Location,Date Purchased,Date Consumed,Price,Hold Until")

currentYear = date.today().year
for bottle in bottles:
	print('"%s","%s",%d,"%s",%.3f,,' % (
		bottle['winery'],
		bottle['label'],
		bottle['vintage'],
		bottle['regionDescription'],
		bottle['abv'] / 100
	), end='')

	for varietal in varietals:
		if varietal[0] in bottle['blend']:
			print("%.2f" % (float(bottle['blend'][varietal[0]]) / 100), end='')

		print(",", end='')

	print(',,"133 - %r",%s,%s,%.2f,%s' % (
		bottle['coord'],
		datetime.strptime(bottle['acquisition'], "%Y-%m-%d").strftime("%m/%d/%y"),
		"" if bottle['consumed'] is None else datetime.strptime(bottle['consumed'], "%Y-%m-%d").strftime("%m/%d/%y"),
		bottle['cost'],
		bottle['holdUntil'] if int(bottle['holdUntil']) > currentYear else "Drink Now"
	))
