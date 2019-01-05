#!/usr/bin/env python3

# This script displays a count of bottles organized by region

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date

from backend.cellar import Cellar
from scripts.styling import stylize

cellar = Cellar()
for data in cellar.byRegion():
	print('%s %s' % (
		stylize(Fore.GREEN, "%2d bottle%s" % (
			len(data['bottles']),
			" " if len(data['bottles']) == 1 else "s")),
		stylize(Style.BRIGHT, data['country'])))

	for region in data['regions']:
		print('%8d bottle%s %s' % (
			len(region['bottles']),
			" " if len(region['bottles']) == 1 else "s",
			stylize(Fore.BLUE, region['region'].name)))

	print()
