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

bottlesPastHold = cellar.bottlesPastHold
labels = {}
totalCost = 0
for bottle in bottlesPastHold:
	labelDesc = "%s  %s  %s" % (
		stylize(Style.BRIGHT, bottle.label.description),
		stylize(Fore.BLUE, bottle.label.varietalDescription),
		stylize(Style.DIM, bottle.label.winery.region.description))

	if showCosts:
		avgPrice = bottle.label.averagePrice(True)
		labelDesc += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % avgPrice)
		totalCost += avgPrice

	if labelDesc not in labels:
		labels[labelDesc] = 1
	else:
		labels[labelDesc] += 1

count = len(bottlesPastHold)
title = "Past Hold: %s" % (
	stylize(Fore.GREEN, '%d bottle%s' % (count, ' ' if count == 1 else 's')))

if showCosts:
	title += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % totalCost)

print(title)

for desc in labels:
	count = labels[desc];
	if count > 1:
		desc += ' ' + stylize(Fore.GREEN, ' (%d bottles)' % count)

	print("      " + desc)
