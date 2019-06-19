#!/usr/bin/env python3

# This script displays the number of bottles consumed each month.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style

from backend.cellar import Cellar
from scripts.styling import stylize
import calendar
import sys

verbose = (len(sys.argv) > 1 and sys.argv[1] == '-v')
cellar = Cellar()

consumption = cellar.consumptionByMonth()
for year in sorted(consumption):
	for month in sorted(consumption[year]):
		count = len(consumption[year][month])

		print("%s: %s" % (
			stylize(Fore.BLUE, "%s %d" % (calendar.month_abbr[month], year)),
			stylize(Fore.GREEN, '%d bottle%s' % (count, ' ' if count == 1 else 's'))))

		if verbose:
			for bottle in consumption[year][month]:
				print("  %s" % bottle.label.description)

			print()

	if verbose:
		print('----------------------------------------\n')

	else:
		print()
