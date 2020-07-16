#!/usr/bin/env python3

# This script displays a count of bottles organized by region

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar
from scripts.styling import stylize

cellar = Cellar()

varietalWidth = 0
longestHold = 0
currentYear = date.today().year

for bottle in cellar.bottles:
	longestHold = max(longestHold, bottle.hold_until)

byVarietal = cellar.byVarietal();
for bucket in byVarietal:
	for data in bucket['data']:
		varietalWidth = max(varietalWidth, len(data['varietal'].name))

firstBucket = True
for bucket in byVarietal:
	bucketCount = 0
	for data in bucket['data']:
		bucketCount += data['totalCount']

	print('%s %s' % (
		stylize(Fore.GREEN, '%4.1f bottles' % bucketCount),
		stylize(Style.BRIGHT, '%-*s' % (varietalWidth + 5, bucket['bucketName']))),
		end = '')

	if firstBucket:
		for year in range(currentYear, longestHold + 1):
			print(stylize(Style.BRIGHT, ' %d' % year), end='')

		print(stylize(Style.BRIGHT, ' |'), end='')

		for year in range(currentYear, longestHold + 1):
			print(stylize(Style.BRIGHT, ' %d' % year), end='')

		firstBucket = False

	print()
	for data in bucket['data']:
		print('%8.1f bottles %s' % (
			data['totalCount'],
			stylize(Fore.BLUE, '%-*s' % (varietalWidth, data['varietal'].name))),
			end = '')

		for year in range(currentYear, longestHold + 1):
			if year in data['pureCountByYear'] and data['pureCountByYear'][year] > 0:
				print(stylize(Fore.GREEN, ' %4d' % data['pureCountByYear'][year]), end = '')

			else:
				print(' %4s' % '.', end = '')

		print(stylize(Style.BRIGHT, '  |'), end = '')

		for year in range(currentYear, longestHold + 1):
			if year in data['blendCountByYear'] and data['blendCountByYear'][year] > 0:
				print(stylize(Fore.GREEN, ' %4.1f' % data['blendCountByYear'][year]), end = '')

			else:
				print(' %4s' % '.', end = '')

		print()
	print()
