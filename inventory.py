#!/usr/bin/env python3

from colorama import Fore, Back, Style
from datetime import date

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name, region.name, region.country FROM label " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "LEFT JOIN region ON winery.region = region.id " +
                        "ORDER BY winery.name, label.name, label.vintage").fetchall()

labels = []
for label in labelData:
	blend = sql.execute("SELECT varietal.name, varietal.boldness, portion FROM blends " +
	                    "LEFT JOIN varietal ON blends.varietal = varietal.id " +
	                    "WHERE blends.label = ? " +
	                    "ORDER BY portion DESC", (label[0],)).fetchall()

	bottleCount = sql.execute("SELECT hold_until, COUNT(id) FROM bottle " +
	                          "WHERE label = ? AND consumption IS NULL " +
	                          "GROUP BY hold_until " +
	                          "ORDER BY hold_until", (label[0],)).fetchall();

	weightedBoldness = [b[1] * b[2] / 100.0 for b in blend]

	if len(blend) == 1:
		varietalDescription = blend[0][0]
	else:
		varietalDescription = ('(' + ', '.join(["%d%% %s" % (b[2], b[0]) for b in sorted(blend, key=lambda bl: bl[2], reverse=True)]) + ')')

	if len(bottleCount) > 0:
		labels.append({
			'labelDescription': str(label[1]) + ' ' + label[2] + ' ' + label[3],
			'regionDescription': label[4] + ', ' + label[5],
			'varietalDescription': varietalDescription,
			'boldness': sum(weightedBoldness) / len(weightedBoldness),
			'bottleCount': bottleCount
		})

currentYear = date.today().year
for label in sorted(labels, key=lambda l: l['boldness'], reverse=True):
	print("%s  %s  %s" % (
		(Style.BRIGHT + label['labelDescription'] + Style.RESET_ALL),
		(Fore.BLUE + label['varietalDescription'] + Style.RESET_ALL),
		(Style.DIM + label['regionDescription'] + Style.RESET_ALL)))

	print(Fore.GREEN, end='')
	for holdYear, holdAmt in label['bottleCount']:
		print('  %d bottle%s to %s' % (
			holdAmt, '' if holdAmt == 1 else 's',
			'drink now' if holdYear == currentYear else ('hold until %d' % holdYear)))
	print(Style.RESET_ALL)
