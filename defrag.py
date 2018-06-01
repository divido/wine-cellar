#!/usr/bin/env python3

from colorama import Fore, Back, Style
from datetime import date

from bottlePlacement import buildLayout, addBottle

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

# --------------------------------------------------------------------------------
# Data Input

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name FROM label " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "ORDER BY winery.name, label.name, label.vintage").fetchall()

currentYear = date.today().year
allCosts = []
allBoldness = []
allHold = []

bottles = []
for label in labelData:
	blend = sql.execute("SELECT varietal.name, varietal.boldness, portion FROM blends " +
	                    "LEFT JOIN varietal ON blends.varietal = varietal.id " +
	                    "WHERE blends.label = ? " +
	                    "ORDER BY portion DESC", (label[0],)).fetchall()

	bottleData = sql.execute("SELECT id, cost, hold_until FROM bottle " +
	                         "WHERE label = ? AND consumption IS NULL", (label[0],)).fetchall();

	weightedBoldness = sum([b[1] * b[2] / 100.0 for b in blend])

	for bottle in bottleData:
		allCosts.append(bottle[1])
		allBoldness.append(weightedBoldness)
		if (bottle[2] > currentYear):
			allHold.append(bottle[2])

		bottles.append({
			'id': bottle[0],
			'holdUntil': bottle[2],
			'cost': bottle[1],
			'boldness': weightedBoldness,
			'labelDescription': str(label[1]) + ' ' + label[2] + ' ' + label[3]
		})

layout = buildLayout(allCosts, allBoldness, allHold)
for bottle in bottles:
	addBottle(layout, bottle)

for bottle in sorted(bottles, key=lambda c: c['coord']):
	print("%sB %4.1f%s  %s$ %6.2f%s  %sH %d%s -- (%2d, %2d, %2d) -- %s" % (
		Style.DIM, bottle['boldness'], Style.RESET_ALL,
		Fore.BLUE, bottle['cost'], Style.RESET_ALL,
		Fore.GREEN, bottle['holdUntil'], Style.RESET_ALL,
		bottle['coord'][0], bottle['coord'][1], bottle['coord'][2],
		Style.BRIGHT + bottle['labelDescription'] + Style.RESET_ALL
	))

while True:
	confirm = input("Commit [y/n]? ")
	if confirm == 'n':
		break

	if confirm == 'y':
		for bottle in bottles:
			coord = bottle['coord']
			sql.execute("UPDATE bottle " +
			            "SET boldness_coord = ?, " +
			            "    price_coord = ?, " +
			            "    hold_coord = ? " +
			            "WHERE id = ?", (coord[0], coord[1], coord[2], bottle['id']))
		db.commit()
		break
