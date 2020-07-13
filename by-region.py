#!/usr/bin/env python3

# This script displays a count of bottles organized by region

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar
from scripts.styling import stylize

cellar = Cellar()

regionWidth = 0
longestHold = 0
currentYear = date.today().year

for bottle in cellar.bottles:
	longestHold = max(longestHold, bottle.hold_until)

byRegion = cellar.byRegion();
for data in byRegion:
	for region in data['regions']:
		regionWidth = max(regionWidth, len(region['region'].name))

firstRegion = True
for data in byRegion:
	print('%s %s' % (
		stylize(Fore.GREEN, '%2d bottle%s' % (
			len(data['bottles']),
			' ' if len(data['bottles']) == 1 else 's')),
		stylize(Style.BRIGHT, '%-*s' % (regionWidth + 8, data['country']))),
		end = '')

	if firstRegion:
		for year in range(currentYear, longestHold + 1):
			print(stylize(Style.BRIGHT, '%d ' % year), end='')

		firstRegion = False

	print()
	for region in data['regions']:
		print('%8d bottle%s %s' % (
			len(region['bottles']),
			' ' if len(region['bottles']) == 1 else 's',
			stylize(Fore.BLUE, '%-*s' % (regionWidth, region['region'].name))),
			end = '')

		inventoryByYear = region['region'].inventoryByYear();
		for year in range(currentYear, longestHold + 1):
			if year in inventoryByYear and inventoryByYear[year] > 0:
				print(stylize(Fore.GREEN, ' %4d' % inventoryByYear[year]), end = '')

			else:
				print(' %4s' % '.', end = '')

		print()
	print()
