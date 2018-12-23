#!/usr/bin/env python3

# This script displays the number of bottles held for each year, and how much
# excess or shortfall there will be in that year.

# --------------------------------------------------------------------------------
from colorama import Fore, Back, Style
from backend.cellar import Cellar

cellar = Cellar()

def stylize(fmt, value):
	return fmt + value + Style.RESET_ALL

# --------------------

projection = cellar.consumptionProjection();

def showField(name, amt):
	print('%s: %s' % (
		stylize(Style.BRIGHT, name),
		stylize(Fore.BLUE, '%d bottle%s' % (amt, '' if amt == 1 else 's'))))

showField('Average Annual Consumption', projection['averageAnnualConsumption'])
showField('Total Bottle Count', projection['totalBottleCount'])
print()

for holdYear in projection['byYear']:
	count = projection['byYear'][holdYear]['count']
	excess = projection['byYear'][holdYear]['excess']

	if excess >= 0:
		excessText = stylize(Fore.BLUE, '%2d Extra' % excess)
	else:
		excessText = '%2d Short' % -excess

	print('%s: %s (%s)' % (
		stylize(Style.BRIGHT, str(holdYear)),
		stylize(Fore.GREEN, '%2d bottle%s' % (count, ' ' if count == 1 else 's')),
		excessText))
