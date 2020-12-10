from colorama import Fore, Back, Style
from datetime import date

from scripts.styling import stylize

class DatabaseLogger:
	"""This class stores changes made to database objects, and prints them out
	on request. It is used by the interactive scripts before confirm
	(committing) data changes.
	"""

	_changes = False
	_newRegions = set()
	_newWineries = set()
	_newLabels = set()
	_newVarietals = set()
	_newBottles = set()
	_bottleConsumptions = set()
	_bottlePositions = set()
	_labelWineries = set()

	# --------------------------------------------------------------------------------

	def newRegion(self, region):
		"""This indicates a new region has been created"""
		self._newRegions.add(region)
		self._changes = True

	def newWinery(self, winery):
		"""This indicates a new winery has been created"""
		self._newWineries.add(winery)
		self._changes = True

	def newLabel(self, label):
		"""This indicates a new label has been created"""
		self._newLabels.add(label)
		self._changes = True

	def newVarietal(self, varietal):
		"""This indicates a new varietal has been created"""
		self._newVarietals.add(varietal)
		self._changes = True

	def newBottle(self, bottle):
		"""This indicates a new bottle has been created"""
		self._newBottles.add(bottle)
		self._changes = True

	def consumedBottle(self, bottle):
		"""This indicates the bottle has been consumed"""
		self._bottleConsumptions.add(bottle)
		self._changes = True

	def changedBottlePosition(self, bottle):
		"""This indicates the bottle has changed position"""
		self._bottlePositions.add(bottle)
		self._changes = True

	def changedLabelWinery(self, label):
		"""This indicates the label has changed wineries"""
		self._labelWineries.add(label)
		self._changes = True

	# --------------------------------------------------------------------------------

	def printChanges(self):
		"""This prints all changes that have been made to the database, adding a
		separating line between each section (if content is actually printed).
		"""

		self._printClearedPositions()
		self._printNewRegions()
		self._printNewWineries()
		self._printNewLabels()
		self._printNewVarietals()
		self._printNewBottles()
		self._printBottleConsumptions()
		self._printChangedPositions()
		self._printChangedWineries()

	def hasChanges(self):
		"""This returns whether there are any changes or not."""

		return self._changes

	# --------------------------------------------------------------------------------

	def _printClearedPositions(self):
		"""Print all bottles that have had their positions cleared. This
		indicates the bottle is no longer stored in any particular location of
		the cellar. Such bottles are likely errors in the placement algorihms,
		so this output is highlighted in red.
		"""

		for bottle in self._bottlePositions:
			if bottle.boldness_coord == None and bottle.price_coord == None and bottle.hold_coord == None:
				print("%s %s" % (
					stylize(Fore.RED, "Clear position for"),
					stylize(Style.BRIGHT, bottle.label.description)))

	def _printNewRegions(self):
		"""Print all regions that have been added this session"""

		for region in self._newRegions:
			print("%s %s" % (
				stylize(Fore.GREEN, "Create New Region:"),
				stylize(Style.BRIGHT, region.description)))

	def _printNewWineries(self):
		"""Print all wineries that have been added this session"""

		for winery in self._newWineries:
			print("%s %s in %s" % (
				stylize(Fore.GREEN, "Create New Winery:"),
				stylize(Style.BRIGHT, winery.name),
				stylize(Style.BRIGHT, winery.region.description)))

	def _printNewLabels(self):
		"""Print all labels that have been added this session"""

		for label in self._newLabels:
			print("%s %s, %s, %s%% abv" % (
				stylize(Fore.GREEN, "Create New Label:"),
				stylize(Style.BRIGHT, label.description),
				stylize(Style.BRIGHT, label.varietalDescription),
				stylize(Style.BRIGHT, ("%.1f" % label.abv))))

	def _printNewVarietals(self):
		"""Print all varietals that have been added this session"""

		for varietal in self._newVarietals:
			print("%s %s, boldness %s" % (
				stylize(Fore.GREEN, "Create New Varietal:"),
				stylize(Style.BRIGHT, varietal.name),
				stylize(Style.BRIGHT, str(varietal.boldness))))

	def _splitByLabel(self, bottles):
		"""This is used by _printNewBottles to divide the incoming bottles by
		label. It returns a mapping of labels to arrays of bottles from that
		label.
		"""

		labels = {}

		for bottle in bottles:
			if bottle.label not in labels:
				labels[bottle.label] = []

			labels[bottle.label].append(bottle)

		return labels

	def _countHoldYears(self, bottles):
		"""This is used by _printNewBottles to divide the incoming bottles of
		the same label by their hold year. It returns a mapping of hold years to
		a number of bottles to be released that year.
		"""
		years = {}

		for bottle in bottles:
			if bottle.hold_until not in years:
				years[bottle.hold_until] = 0

			years[bottle.hold_until] += 1

		return years

	def _printNewBottles(self):
		"""Print all bottles that have been added this session"""

		currentYear = date.today().year
		needSeparator = False
		for label, bottles in self._splitByLabel(self._newBottles).items():
			if needSeparator: print()
			needSeparator = True

			print("%s %s" % (
				stylize(Fore.GREEN, ("Create New Bottle%s" % ("" if len(bottles) == 1 else "s"))),
				stylize(Style.BRIGHT, label.description)))

			counts = self._countHoldYears(bottles)
			for holdYear in sorted(counts):
				holdAmt = counts[holdYear]

				print(stylize(Fore.BLUE, "  %d bottle%s to %s" % (
					holdAmt, ("" if holdAmt == 1 else "s"),
					"Drink Now" if holdYear == currentYear else (
						"Hold Until %d" % holdYear))))

	def _printBottleConsumptions(self):
		"""Print all bottles that have been consumed"""

		for bottle in self._bottleConsumptions:
			print("%s %s, %s %s, %s %s" % (
				stylize(Fore.RED, "Consumed"),
				stylize(Style.BRIGHT, bottle.label.description),
				stylize(Fore.RED, "stored at"),
				stylize(Style.BRIGHT, "(%d, %d, %d)" % (
					bottle.boldness_coord,
					bottle.price_coord,
					bottle.hold_coord)),
				stylize(Fore.RED, "on"),
				stylize(Style.BRIGHT, bottle.consumption.strftime('%Y-%m-%d'))))

	def _printChangedPositions(self):
		"""Print all bottles that have had their positions changed."""

		lastStack=None
		lastRow=None
		for bottle in sorted(self._bottlePositions, key=lambda b: (b.coordinate[0], b.coordinate[1], -b.coordinate[2])):
			if bottle.boldness_coord != None or bottle.price_coord != None or bottle.hold_coord != None:
				if bottle.boldness_coord != lastStack:
					print(stylize(Fore.GREEN, '\n-------- Stack %d --------------------------------' % bottle.boldness_coord))

				elif bottle.price_coord != lastRow:
					print('')

				lastStack = bottle.boldness_coord
				lastRow = bottle.price_coord

				print("%s %s %s" % (
					stylize(Fore.BLUE, "Move"),
					stylize(Style.BRIGHT, bottle.label.description),
					stylize(Fore.BLUE, "to (%d, %d, %d)" % (
						bottle.boldness_coord,
						bottle.price_coord,
						bottle.hold_coord))))

	def _printChangedWineries(self):
		"""Print all labels that have had their wineries changed. Includes the
		region, since this is expected to be used when splitting a region"""

		for label in self._labelWineries:
			print("%s %s (%s)" % (
				stylize(Fore.GREEN, "Change Winery:"),
				stylize(Style.BRIGHT, label.description),
				stylize(Style.DIM, label.winery.region.description)))
