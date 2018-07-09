#!/usr/bin/env python3

import os
from colorama import Fore, Back, Style
from datetime import date

from bottlePlacement import buildLayout, addExistingBottle, addBottle

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name FROM label " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "ORDER BY winery.name, label.name, label.vintage").fetchall()

currentYear = date.today().year

# Probably don't need these, but generate them anyway..
allCosts = []
allBoldness = []
allHold = []

bottles = []
for label in labelData:
	blend = sql.execute("SELECT varietal.name, varietal.boldness, portion FROM blends " +
	                    "LEFT JOIN varietal ON blends.varietal = varietal.id " +
	                    "WHERE blends.label = ? " +
	                    "ORDER BY portion DESC", (label[0],)).fetchall()

	bottleData = sql.execute("SELECT id, cost, hold_until, boldness_coord, price_coord, hold_coord FROM bottle " +
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
			'currentCoord': (bottle[3], bottle[4], bottle[5]),
			'coord': (bottle[3], bottle[4], bottle[5]),
			'labelDescription': str(label[1]) + ' ' + label[2] + ' ' + label[3]
		})

layout = buildLayout(allCosts, allBoldness, allHold)
for bottle in bottles:
	coord = bottle['coord']
	if not (coord[0] is None or coord[1] is None or coord[2] is None):
		addExistingBottle(layout, bottle)

for bottle in bottles:
	coord = bottle['coord']
	if coord[0] is None or coord[1] is None or coord[2] is None:
		addBottle(layout, bottle)

for bottle in bottles:
	if bottle['coord'] != bottle['currentCoord']:
		coord = bottle['coord']
		newBottle = (coord[0] is None or coord[1] is None or coord[2] is None)
		print('%s%s %s%s%s to %s%r%s' % (
			(Fore.BLUE + "Add") if newBottle else (Fore.GREEN + "Move"),
			Style.RESET_ALL,
			Style.BRIGHT, bottle['labelDescription'], Style.RESET_ALL,
			Fore.BLUE if newBottle else Fore.GREEN,
			bottle['coord'],
			Style.RESET_ALL))

while True:
	confirm = input("Commit [y/n]? ")
	if confirm == 'n':
		break

	if confirm == 'y':
		for bottle in bottles:
			if bottle['coord'] != bottle['currentCoord']:
				coord = bottle['coord']
				sql.execute("UPDATE bottle " +
				            "SET boldness_coord = ?, " +
				            "    price_coord = ?, " +
				            "    hold_coord = ? " +
				            "WHERE id = ?", (coord[0], coord[1], coord[2], bottle['id']))
		db.commit()
		break

