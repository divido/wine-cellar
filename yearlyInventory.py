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

bottlesByYear = cellar.bottlesByYear
for year in sorted(bottlesByYear):
	bottles = bottlesByYear[year]
	count = len(bottles)
	yearCost = 0

	labels = {}
	for bottle in bottles:
		labelDesc = "%s  %s  %s" % (
			stylize(Style.BRIGHT, bottle.label.description),
			stylize(Fore.BLUE, bottle.label.varietalDescription),
			stylize(Style.DIM, bottle.label.winery.region.description))

		if showCosts:
			avgPrice = bottle.label.averagePrice(True)
			labelDesc += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % avgPrice)
			yearCost += avgPrice

		if labelDesc not in labels:
			labels[labelDesc] = 1
		else:
			labels[labelDesc] += 1

	yearDesc = "%s: %s" % (
		stylize(Fore.BLUE, "%d" % year),
		stylize(Fore.GREEN, '%d bottle%s' % (count, ' ' if count == 1 else 's')))

	if showCosts:
		yearDesc += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % yearCost)

	print(yearDesc)

	for desc in labels:
		count = labels[desc];
		if count > 1:
			desc += ' ' +stylize(Fore.GREEN, ' (%d bottles)' % count)

		print("      " + desc)

	print()
