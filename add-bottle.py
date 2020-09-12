#!/usr/bin/env python3

# This script adds a new bottle to the cellar, leaving it unpositioned. Along
# the way, it may also create new regions, varietals, blends, etc.

# --------------------------------------------------------------------------------

from colorama import Fore, Back, Style
from datetime import date
from dateutil.parser import parse
from operator import attrgetter

from backend.raw import db
from backend.repository import Repository
from scripts.styling import stylize
from scripts.fuzzyMatchTextEntry import textEntry
from scripts.confirm import confirmAndCommit

# --------------------------------------------------------------------------------
# Data Input

def getRegion(repo):
	"""This prompts the user to select a region from the list of all known
	regions, or enter a new one.
	"""
	while True:
		idx, region = textEntry("  Region> ", [region.description for region in repo.regions])

		if idx is not None:
			return repo.regions[idx]

		parts = region.split(',')
		if len(parts) == 2:
			return repo.addRegion(parts[0].strip(), parts[1].strip())

		print("Region should have exactly one comma: RegionName, Country")

# ----------------------------------------

def disambiguateRegion(repo, matchingWineries):
	"""This selects which winery among multiples with the same name"""

	print("\nMultiple Regions for %s:" % stylize(Style.BRIGHT, matchingWineries[0].name))
	for winery in matchingWineries:
		print("  " + stylize(Style.DIM, winery.region.description))

	print()
	region = getRegion(repo)

	for winery in matchingWineries:
		if winery.region is region:
			return winery

	return repo.addWinery(winery, region)

# ----------------------------------------

def getWinery(repo):
	"""This prompts the user to select a winery from the list of all current
	wineries, or to enter a new one.
	"""

	idx, winery = textEntry("Winery> ", [winery.name for winery in repo.wineries])
	if idx is not None:
		# Check to see if multiple wineries have the same name (happens when a
		# winery is split into multiple regions)
		matchingWineries = []
		for w in repo.wineries:
			if w.name == winery:
				matchingWineries.append(w)

		if len(matchingWineries) == 1:
			return repo.wineries[idx]

		return disambiguateRegion(repo, matchingWineries)

	print('\n*** New Winery ***')
	return repo.addWinery(winery, getRegion(repo))

# ----------------------------------------

def getVarietalPortions(repo):
	"""This prompts the user to create the appropriate blend of grape varietals"""

	varietalPortions = []
	remaining = 100
	while remaining > 0:
		idx, varietalName = textEntry("  Varietal> ", [varietal.name for varietal in repo.varietals])

		if idx is not None:
			varietal = repo.varietals[idx]
		else:
			boldness = None
			while boldness is None:
				boldnessStr = textEntry("    Boldness (? to list current)> ", [])[1];

				if boldnessStr == '?':
					for varietal in sorted(repo.varietals, key=attrgetter('boldness'), reverse=True):
						print('      %s %s' % (
							stylize(Fore.BLUE, '%2d' % varietal.boldness),
							stylize(Style.BRIGHT, '%s' % varietal.name)))

				else:
					boldness = int(boldnessStr)

			varietal = repo.addVarietal(varietalName, boldness)

		portionStr = textEntry("  Percentage (* for remainder)> ", [])[1];
		if portionStr == '*':
			portion = remaining

		else:
			portion = min(remaining, int(portionStr))

		varietalPortions.append((varietal, portion))
		remaining -= portion;
		if remaining > 0: print()

	return varietalPortions

# ----------------------------------------

def getLabel(repo, winery):
	"""This prompts the user to select a label from the list of all those known
	from the selected winery, or enter a new one.
	"""

	labelName = textEntry("Label> ", [label.name for label in winery.labels])[1]
	vintage = int(textEntry("Vintage> ", [])[1])

	label = repo.findLabel(winery, labelName, vintage)
	if label is not None:
		return label

	print('\n*** New Label ***')
	abv = float(textEntry("  ABV> ", [])[1])
	print()

	return repo.addLabel(labelName, vintage, abv, winery, getVarietalPortions(repo))

# ----------------------------------------

def addBottles(repo, label):
	"""This prompts the user for details about the recently acquired bottles
	that are associated with the supplied label.
	"""

	cost = float(textEntry("Cost> ", [])[1])
	acquisition = parse(textEntry("Acquisition Date> ", [])[1])

	print('\nSpace separated list of desired bottle ages, with multipliers, e.g.: 3*0 10 12 15')
	holdEncoding = textEntry("Hold Until Aged> ", [])[1]

	currentYear = date.today().year
	holdYears = {}
	for part in holdEncoding.split():
		subparts = part.split('*')

		if len(subparts) == 1:
			num = 1
			age = int(subparts[0])

		else:
			num = int(subparts[0])
			age = int(subparts[1])

		year = max(currentYear, label.vintage + age)
		if year in holdYears:
			holdYears[year] += num

		else:
			holdYears[year] = num

	for holdYear in sorted(holdYears):
		holdAmt = holdYears[holdYear]

		for i in range(0, holdAmt):
			repo.addBottle(cost, acquisition, holdYear, label)

# --------------------------------------------------------------------------------

repo = Repository()
winery = getWinery(repo)
print()

label = getLabel(repo, winery)
print()

addBottles(repo, label)
print()

confirmAndCommit(db, repo.logger)
