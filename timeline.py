#!/usr/bin/env python3

from colorama import Fore, Back, Style
from datetime import date
from dateutil.parser import parse

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

bottleData = sql.execute("SELECT COUNT(consumption), MIN(consumption), MAX(consumption) FROM bottle " +
                         "WHERE consumption IS NOT NULL").fetchone()

numYears = (parse(bottleData[2]) - parse(bottleData[1])).days / 365;
bottlesPerYear = round(bottleData[0] / numYears)

# ----------------------------------------

labelData = sql.execute("SELECT label.id FROM label").fetchall()
countByYear = {}

totalBottles = 0
currentYear = date.today().year
maxYear = currentYear
labels = []
for label in labelData:
	bottleCount = sql.execute("SELECT hold_until, COUNT(id) FROM bottle " +
	                          "WHERE label = ? AND consumption IS NULL " +
	                          "GROUP BY hold_until", (label[0],)).fetchall()

	for holdYear, holdAmt in bottleCount:
		if holdYear <= currentYear:
			holdYear = currentYear

		maxYear = max(maxYear, holdYear)

		if holdYear not in countByYear:
			countByYear[holdYear] = 0
		countByYear[holdYear] += holdAmt

		totalBottles += holdAmt

# ----------------------------------------

carryover = 0
print('%sAverage Annual Consumption%s: %s%d bottles%s' % (
	Style.BRIGHT, Style.RESET_ALL,
	Fore.BLUE, bottlesPerYear, Style.RESET_ALL))

print('%sTotal Bottle Count%s: %s%d bottles%s\n' % (
	Style.BRIGHT, Style.RESET_ALL,
	Fore.BLUE, totalBottles, Style.RESET_ALL))

for holdYear in range(currentYear, maxYear + 1):
	holdAmt = countByYear[holdYear] if holdYear in countByYear else 0
	expectedConsumption = bottlesPerYear

	if holdYear == currentYear:
		daysLeft = (date(currentYear + 1, 1, 1) - date.today()).days
		expectedConsumption = round(bottlesPerYear * daysLeft / 365)

	excessBottles = (holdAmt + carryover) - expectedConsumption
	carryover = max(excessBottles, 0)

	excessStyle = Fore.BLUE if excessBottles >= 0 else ''
	excessText = 'Extra' if excessBottles >= 0 else 'Short'

	print('%s%d%s: %s%2d bottle%s%s (%s%2d %s%s)' % (
		Style.BRIGHT, holdYear, Style.RESET_ALL,
		Fore.GREEN, holdAmt, ' ' if holdAmt == 1 else 's', Style.RESET_ALL,
		excessStyle, abs(excessBottles), excessText, Style.RESET_ALL))
