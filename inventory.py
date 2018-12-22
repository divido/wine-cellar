#!/usr/bin/env python3

# This script displays a list of all owned labels, and how many bottles of each
# are currently in the cellar. Bottle lists are categorized by hold year.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar

cellar = Cellar()

def stylize(fmt, value):
	return fmt + value + Style.RESET_ALL

currentYear = date.today().year
for label in sorted(cellar.labels, key=lambda l: l.weightedBoldness, reverse=True):
	print("%s  %s  %s" % (
		stylize(Style.BRIGHT, label.description),
		stylize(Fore.BLUE, label.varietalDescription),
		stylize(Style.DIM, label.winery.region.description)))

	inventoryByYear = label.inventoryByYear()
	for holdYear in sorted(inventoryByYear):
		holdAmt = inventoryByYear[holdYear]
		print(stylize(Fore.GREEN, '  %d bottle%s to %s' % (
			holdAmt, '' if holdAmt == 1 else 's',
			'drink now' if holdYear == currentYear else ('hold until %d' % holdYear))))

	print()
