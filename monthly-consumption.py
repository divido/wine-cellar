#!/usr/bin/env python3

# This script displays the number of bottles consumed each month.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style

from backend.cellar import Cellar
from scripts.styling import stylize
from scripts.options import parseArguments
import calendar

[verbose, showCosts] = parseArguments([
	('v', 'verbose', 'Also show specific bottles'),
	('c', 'cost', 'Also show bottle costs')
])

cellar = Cellar()

consumption = cellar.consumptionByMonth()
for year in sorted(consumption):
	for month in sorted(consumption[year]):
		count = len(consumption[year][month])

		monthSummary = ("%s: %s" % (
			stylize(Fore.BLUE, "%s %d" % (calendar.month_abbr[month], year)),
			stylize(Fore.GREEN, '%d bottle%s' % (count, ' ' if count == 1 else 's'))))

		if showCosts:
			totalCost = 0
			for bottle in consumption[year][month]:
				totalCost += bottle.cost

			monthSummary += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % totalCost)

		print(monthSummary)

		if verbose:
			for bottle in consumption[year][month]:
				desc = "  " + bottle.label.description
				if showCosts:
					desc += "  " + stylize(Style.DIM, "$%.2f" % bottle.cost)

				print(desc)

			print()

	if verbose:
		print('----------------------------------------\n')

	else:
		print()
