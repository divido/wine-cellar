#!/usr/bin/env python3

# This script allows the user to find and mark a bottle as consumed

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from dateutil.parser import parse
from datetime import date

from backend.raw import db
from backend.cellar import Cellar
from scripts.styling import stylize
from scripts.fuzzyMatchTextEntry import textEntry
from scripts.confirm import confirmAndCommit
from scripts.options import parseArguments

[all] = parseArguments([('a', 'all', 'Consider all bottles, regardless of hold date')])

currentYear = date.today().year

cellar = Cellar()

if all:
	bottles = cellar.bottles
else:
	bottles = cellar.bottlesByYear[currentYear]

while True:
	idx, name = textEntry("Bottle> ", [bottle.label.description for bottle in bottles])

	if idx is not None:
		break

	print('\nYou must tab-select one of the autocomplete options')

consumption = parse(textEntry("Consumption Date> ", [])[1])
print()

cellar.consume(bottles[idx], consumption)
confirmAndCommit(db, cellar.logger)
