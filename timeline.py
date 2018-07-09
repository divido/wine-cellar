#!/usr/bin/env python3

from colorama import Fore, Back, Style
from datetime import date

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

labelData = sql.execute("SELECT label.id FROM label").fetchall()
countByYear = {}

currentYear = date.today().year
maxYear = currentYear
labels = []
for label in labelData:
	bottleCount = sql.execute("SELECT hold_until, COUNT(id) FROM bottle " +
	                          "WHERE label = ? AND consumption IS NULL " +
	                          "GROUP BY hold_until", (label[0],)).fetchall();

	for holdYear, holdAmt in bottleCount:
		if holdYear <= currentYear:
			holdYear = currentYear

		maxYear = max(maxYear, holdYear)

		if holdYear not in countByYear:
			countByYear[holdYear] = 0
		countByYear[holdYear] += holdAmt

for holdYear in range(currentYear, maxYear + 1):
	holdAmt = countByYear[holdYear] if holdYear in countByYear else 0
	print('%s%d%s: %s%2d bottle%s%s' % (
		Style.BRIGHT, holdYear, Style.RESET_ALL,
		Fore.GREEN, holdAmt, '' if holdAmt == 1 else 's', Style.RESET_ALL))
