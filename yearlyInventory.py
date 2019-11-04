#!/usr/bin/env python3

# This script displays a list of all owned labels, and how many bottles of each
# are currently in the cellar. Bottle lists are categorized by hold year.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar
from scripts.styling import stylize

cellar = Cellar()

bottlesByYear = cellar.bottlesByYear
for year in sorted(bottlesByYear):
	bottles = bottlesByYear[year]
	count = len(bottles)

	print("%s: %s" % (
		stylize(Fore.BLUE, "%d" % year),
		stylize(Fore.GREEN, '%d bottle%s' % (count, ' ' if count == 1 else 's'))))

	labels = {}
	for bottle in bottles:
		labelDesc = "%s  %s  %s" % (
			stylize(Style.BRIGHT, bottle.label.description),
			stylize(Fore.BLUE, bottle.label.varietalDescription),
			stylize(Style.DIM, bottle.label.winery.region.description))

		if labelDesc not in labels:
			labels[labelDesc] = 1
		else:
			labels[labelDesc] += 1

	for desc in labels:
		count = labels[desc];
		countStr = ""
		if count > 1:
			countStr = stylize(Fore.GREEN, ' (%d bottles)' % count)

		print("      %s %s" % (desc, countStr))

	print()
