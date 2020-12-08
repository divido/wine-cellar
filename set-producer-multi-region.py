#!/usr/bin/env python3

# This script queries for a particular producer, listing everything ever owned
# by that vintner

# --------------------------------------------------------------------------------

from datetime import date
from colorama import Fore, Style

from backend.raw import db
from backend.repository import Repository
from scripts.styling import stylize
from scripts.fuzzyMatchTextEntry import textEntry
from scripts.options import parseArguments
from scripts.confirm import confirmAndCommit

# --------------------------------------------------------------------------------
# Data Input

def getRegion(repo, defaultRegion):
	"""This prompts the user to select a region from the list of all known
	regions, or enter a new one.
	"""
	while True:
		idx, region = textEntry("  Region> ", [region.description for region in repo.regions])

		if idx is not None:
			return repo.regions[idx]

		if region == "":
			return defaultRegion

		parts = region.split(',')
		if len(parts) == 2:
			return repo.addRegion(parts[0].strip(), parts[1].strip())

		print("Region should have exactly one comma: RegionName, Country")

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
wineryName = getWinery(repo).name
print()
print(stylize(Style.BRIGHT, "Current Regions:"))

matchingWineries = []
labels = []
for winery in repo.wineries:
	if winery.name == wineryName:
		print("  " + winery.region.description)
		matchingWineries.append(winery)
		labels += winery.labels

for label in labels:
	print()
	print("%s  %s  %s" % (
		stylize(Style.BRIGHT, label.description),
		stylize(Fore.BLUE, label.varietalDescription),
		stylize(Style.DIM, label.winery.region.description)))

	region = getRegion(repo, label.winery.region)
	if region is not label.winery.region:
		for winery in matchingWineries:
			if region is winery.region:
				repo.changeLabelWinery(label, winery)
				break

		else: # Else here means "if loop completed without hitting a break statement"
			winery = repo.addWinery(wineryName, region)
			repo.changeLabelWinery(label, winery)

confirmAndCommit(db, repo.logger)
