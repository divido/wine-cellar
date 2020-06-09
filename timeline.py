#!/usr/bin/env python3

# This script displays the number of bottles held for each year, and how much
# excess or shortfall there will be in that year.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style

from backend.cellar import Cellar
from scripts.styling import stylize
from scripts.options import parseArguments

[showCosts] = parseArguments([('c', 'cost', 'Also show total inventory value')])
cellar = Cellar()
projection = cellar.consumptionProjection();

def showBottleCount(name, amt):
	print('%s: %s' % (
		stylize(Style.BRIGHT, name),
		stylize(Fore.BLUE, '%d bottle%s' % (amt, '' if amt == 1 else 's'))))

def showDollarValue(name, amt):
	print('%s: %s' % (
		stylize(Style.BRIGHT, name),
		stylize(Fore.GREEN, '$%.2f' % amt)))

showBottleCount('Average Annual Consumption', projection['averageAnnualConsumption'])
showBottleCount('Total Stored Bottle Count', projection['numStored'])
print()

if showCosts:
	showDollarValue('Average Consumed Bottle Value', projection['averageConsumedBottleValue'])
	showDollarValue('Average Stored Bottle Value', projection['valueStored'] / projection['numStored'])
	showDollarValue('Total Stored Value', projection['valueStored'])
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
