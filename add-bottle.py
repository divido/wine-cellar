#!/usr/bin/env python3

from fuzzyMatchTextEntry import textEntry
from colorama import Fore, Back, Style
from datetime import date
from dateutil.parser import parse

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

# --------------------------------------------------------------------------------
# Data Input

wineries = sql.execute('SELECT id, name FROM winery').fetchall()
winery_idx, winery = textEntry("Winery> ", [w[1] for w in wineries])

if winery_idx is None:
	print('\n*** New Winery ***')
	regions = sql.execute('SELECT id, name, country FROM region').fetchall()

	while True:
		region_idx, region = textEntry("Region> ", [(r[1] + ', ' + r[2]) for r in regions])

		if len(region.split(',')) == 2:
			break

		print("Region should have exactly one comma: RegionName, Country")
	labels = []
	print()

else:
	winery_id = int(wineries[winery_idx][0])
	labels = sql.execute('SELECT id, name, vintage FROM label WHERE winery=?', (winery_id,)).fetchall()

label_idx = None
label = textEntry("Label> ", [l[1] for l in labels])[1]
vintage = int(textEntry("Vintage> ", [])[1])

for idx, (labelId, labelName, labelVintage) in enumerate(labels):
	if labelName == label and labelVintage == vintage:
		label_idx = idx

if label_idx is None:
	print("\n*** New Label ***")
	varietals = sql.execute('SELECT id, name, boldness FROM varietal').fetchall()

	labelVarietals = []
	remaining = 100
	while remaining > 0:
		varietal_idx, varietal = textEntry("Varietal> ", [v[1] for v in varietals])

		if varietal_idx is None:
			varietal_id = None
			varietal_boldness = int(textEntry("Boldness> ", [])[1])

		else:
			varietal_id = varietals[varietal_idx][0]
			varietal_boldness = varietals[varietal_idx][2]

		portionStr = textEntry("Percentage (* for remainder)> ", [])[1];
		if portionStr == '*':
			portion = remaining

		else:
			portion = min(remaining, int(portionStr))

		labelVarietals.append((varietal_id, varietal, varietal_boldness, portion))
		remaining -= portion;
		print()

	labelVarietals.sort(key=lambda v: v[3], reverse=True)

else:
	label_id = labels[label_idx][0]

cost = float(textEntry("Cost> ", [])[1])
abv = float(textEntry("ABV> ", [])[1])
acquisition = parse(textEntry("Acquisition Date> ", [])[1]).strftime('%Y-%m-%d')

print('\nSpace separated list of desired bottle ages, with multipliers, e.g.: 3*0 10 12 15')
holdEncoding = textEntry("Hold Until Aged> ", [])[1]

currentYear = date.today().year
holdYears = {}
for part in holdEncoding.split():
	subparts = part.split('*')

	if len(subparts) == 1:
		num = 1
		age = int(subparts[0])

	else:
		num = int(subparts[0])
		age = int(subparts[1])

	year = max(currentYear, vintage + age)
	if year in holdYears:
		holdYears[year] += num

	else:
		holdYears[year] = num

# --------------------------------------------------------------------------------
# Print Validation

print(Fore.BLUE)

if winery_idx is None:
	if region_idx is None:
		print("New Region: %s" % region)
	print("New Winery: %s" % winery)

if label_idx is None:
	blend = []
	for varietalId, varietalName, varietalBoldness, varietalPortion in labelVarietals:
		if varietalId is None:
			print("New Varietal: %s, Boldness %d" % (varietalName, varietalBoldness))
		blend.append("%d%% %s" % (varietalPortion, varietalName))

	print("New Label: %d %s, (%s)" % (vintage, label, ', '.join(blend)))

print(Style.RESET_ALL, end='')
print("%s%d %s %s, $%.2f, %.1f%% ABV acquired on %s%s" % (
	Style.BRIGHT, vintage, winery, label, cost, abv, acquisition, Style.RESET_ALL
))

print(Fore.GREEN)
for holdYear in sorted(holdYears):
	holdAmt = holdYears[holdYear]
	print('%d bottle%s to %s' % (
		holdAmt, '' if holdAmt == 1 else 's',
		'drink now' if holdYear == currentYear else ('hold until %d' % holdYear)))
print(Style.RESET_ALL, end='')

# --------------------------------------------------------------------------------
# Execution

while True:
	confirm = input("Commit [y/n]? ")
	if confirm == 'n':
		break

	if confirm == 'y':
		if winery_idx is None:
			if region_idx is None:
				regionName, country = region.split(',')
				sql.execute('INSERT INTO region VALUES (NULL, ?, ?)', (regionName.strip(), country.strip()))
				region_id = sql.lastrowid

			else:
				region_id = regions[region_idx][0]

			sql.execute('INSERT INTO winery VALUES (NULL, ?, ?)', (winery, region_id))
			winery_id = sql.lastrowid

		if label_idx is None:
			sql.execute('INSERT INTO label VALUES (NULL, ?, ?, ?, ?)', (label, winery_id, vintage, abv))
			label_id = sql.lastrowid

			for varietalId, varietalName, varietalBoldness, varietalPortion in labelVarietals:
				if varietalId is None:
					sql.execute('INSERT INTO varietal VALUES (NULL, ?, ?)', (varietalName, varietalBoldness))
					varietalId = sql.lastrowid

				sql.execute('INSERT INTO blends VALUES (?, ?, ?)', (label_id, varietalId, varietalPortion))

		for holdYear in sorted(holdYears):
			holdAmt = holdYears[holdYear]

			for i in range(0, holdAmt):
				sql.execute('INSERT INTO bottle VALUES (NULL, ?, ?, ?, NULL, ?, NULL, NULL, NULL)', (label_id, cost, acquisition, holdYear))

		db.commit()
		break
