#!/usr/bin/env python3

from colorama import Fore, Back, Style
from datetime import date
from dateutil.parser import parse

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

bottleData = sql.execute("SELECT region.name, region.country, bottle.id FROM bottle " +
                         "LEFT JOIN label ON bottle.label = label.id " +
                         "LEFT JOIN winery ON label.winery = winery.id " +
                         "LEFT JOIN region ON winery.region = region.id " +
                         "WHERE consumption IS NULL").fetchall()

# ----------------------------------------

regionCount = {}
countryCount = {}

for bottle in bottleData:
	region = bottle[0]
	country = bottle[1]

	if country not in regionCount:
		regionCount[country] = {}
		countryCount[country] = 0

	if region not in regionCount[country]:
		regionCount[country][region] = 0

	regionCount[country][region] += 1
	countryCount[country] += 1

# ----------------------------------------

for country in sorted(countryCount, key = lambda c: countryCount[c], reverse = True):
	print('%s%2d bottle%s%s %s%s%s' % (
		Fore.GREEN, countryCount[country], ' ' if countryCount[country] == 1 else 's', Style.RESET_ALL,
		Style.BRIGHT, country, Style.RESET_ALL))

	for region in sorted(regionCount[country], key = lambda r: regionCount[country][r], reverse = True):
		print('      %s%2d bottle%s%s %s%s%s' % (
			Style.RESET_ALL, regionCount[country][region], ' ' if regionCount[country][region] == 1 else 's', Style.RESET_ALL,
			Fore.BLUE, region, Style.RESET_ALL))

	print('')
