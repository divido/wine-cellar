#!/usr/bin/env python3

from colorama import Fore, Back, Style
from dateutil.parser import parse

from backend.raw import db
from backend.cellar import Cellar
from scripts.styling import stylize
from scripts.fuzzyMatchTextEntry import textEntry
from scripts.confirm import confirmAndCommit

cellar = Cellar()
bottles = cellar.bottles
while True:
	idx, name = textEntry("Bottle> ", [bottle.label.description for bottle in bottles])

	if idx is not None:
		break

	print('\nYou must tab-select one of the autocomplete options')

consumption = parse(textEntry("Consumption Date> ", [])[1])
print()

cellar.consume(bottles[idx], consumption)
confirmAndCommit(db, cellar.logger)
