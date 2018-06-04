#!/usr/bin/env python3

from fuzzyMatchTextEntry import textEntry
from colorama import Fore, Back, Style
from dateutil.parser import parse

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

# --------------------------------------------------------------------------------
# Data Input

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name, bottle.consumption FROM bottle " +
                        "LEFT JOIN label ON bottle.label = label.id " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "WHERE bottle.consumption IS NULL").fetchall()

while True:
	label_idx, label = textEntry("Bottle> ", [str(l[1]) + ' ' + l[2] + ' ' + l[3] for l in labelData])

	if label_idx is not None:
		label_id = labelData[label_idx][0]
		break

	else:
		print('\nYou must tab-select one of the autocomplete options')

bottle = sql.execute("SELECT bottle.id, hold_until, boldness_coord, price_coord, hold_coord FROM bottle " +
                     "WHERE bottle.label = ? AND consumption IS NULL " +
                     "ORDER BY hold_until LIMIT 1", (label_id,)).fetchone()

consumption = parse(textEntry("Consumption Date> ", [])[1]).strftime('%Y-%m-%d')

print("\nConsumed %s%d %s %s%s, stored at %s%r%s, on %s%s%s" % (
	Style.BRIGHT,
	labelData[label_idx][1], labelData[label_idx][2], labelData[label_idx][3],
	Style.RESET_ALL,

	Fore.BLUE,
	(bottle[2], bottle[3], bottle[4]),
	Style.RESET_ALL,

	Fore.GREEN,
	consumption,
	Style.RESET_ALL
))

while True:
	confirm = input("Commit [y/n]? ")
	if confirm == 'n':
		break

	if confirm == 'y':
		sql.execute('UPDATE bottle SET consumption = ? WHERE id = ?', (consumption, bottle[0]))
		db.commit()
		break
