#!/usr/bin/env python3

# This script displays a list of all owned labels, and how many bottles of each
# are currently in the cellar. Bottle lists are categorized by hold year.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar
from scripts.styling import stylize
from scripts.options import parseArguments

[showCosts] = parseArguments([('c', 'cost', 'Also show bottle costs')])
cellar = Cellar()

currentYear = date.today().year
for label in sorted(cellar.labels, key=lambda l: l.weightedBoldness, reverse=True):
	labelDesc = "%s  %s  %s" % (
		stylize(Style.BRIGHT, label.description),
		stylize(Fore.BLUE, label.varietalDescription),
		stylize(Style.DIM, label.winery.region.description))

	if showCosts:
		labelDesc += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % label.averagePrice(True))

	print(labelDesc)

	inventoryByYear = label.inventoryByYear()
	for holdYear in sorted(inventoryByYear):
		holdAmt = inventoryByYear[holdYear]
		print(stylize(Fore.GREEN, '  %d bottle%s to %s' % (
			holdAmt, '' if holdAmt == 1 else 's',
			'drink now' if holdYear == currentYear else ('hold until %d' % holdYear))))

	print()

if showCosts:
	print(stylize(Style.DIM + Fore.GREEN, "Prices are average costs of remaining (unconsumed) bottles"));
