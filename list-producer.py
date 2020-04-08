#!/usr/bin/env python3

# This script queries for a particular producer, listing everything ever owned
# by that vintner

# --------------------------------------------------------------------------------

from datetime import date
from colorama import Fore, Style

from backend.repository import Repository
from scripts.styling import stylize
from scripts.fuzzyMatchTextEntry import textEntry
from scripts.options import parseArguments

# --------------------------------------------------------------------------------

def getWinery(repo):
	"""This prompts the user to select a winery from the list of all current
	wineries
	"""

	while True:
		idx, winery = textEntry("Winery> ", [winery.name for winery in repo.wineries])
		if idx is not None:
			return repo.wineries[idx]

		print("Unknown entry. Try again")

# --------------------------------------------------------------------------------

[showCosts] = parseArguments([('c', 'cost', 'Also show bottle costs')])
repo = Repository()
winery = getWinery(repo)
print()

currentYear = date.today().year
for label in sorted(winery.labels, key=lambda l: l.weightedBoldness, reverse=True):
	labelDesc = "%s  %s  %s" % (
		stylize(Style.BRIGHT, label.description),
		stylize(Fore.BLUE, label.varietalDescription),
		stylize(Style.DIM, label.winery.region.description))

	if showCosts:
		labelDesc += "  " + stylize(Style.DIM + Fore.GREEN, "$%.2f" % label.averagePrice(False))

	print(labelDesc)

	consumed = label.numberConsumed;
	if (consumed > 0):
		print(stylize(Style.DIM, '  %d bottle%s consumed' % (
			consumed, '' if consumed == 1 else 's')))

	inventoryByYear = label.inventoryByYear()
	for holdYear in sorted(inventoryByYear):
		holdAmt = inventoryByYear[holdYear]
		print(stylize(Fore.GREEN, '  %d bottle%s to %s' % (
			holdAmt, '' if holdAmt == 1 else 's',
			'drink now' if holdYear == currentYear else ('hold until %d' % holdYear))))

	print()

if showCosts:
	print(stylize(Style.DIM + Fore.GREEN, "Prices are average costs of all bottles ever purchased"));
