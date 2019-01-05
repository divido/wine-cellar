from colorama import Fore, Back, Style
from scripts.styling import stylize

class DatabaseLogger:
	"""This class stores changes made to database objects, and prints them out
	on request. It is used by the interactive scripts before confirm
	(committing) data changes.
	"""

	_bottlePositions = set()

	# --------------------------------------------------------------------------------

	def changedBottlePosition(self, bottle):
		"""This indicates the bottle has changed position"""
		self._bottlePositions.add(bottle);

	# --------------------------------------------------------------------------------

	def printChanges(self):
		"""This prints all changes that have been made to the database, adding a
		separating line between each section (if content is actually printed).
		"""

		if self._printClearedPositions() > 0:
			print()

		if self._printChangedPositions() > 0:
			print()

	# --------------------------------------------------------------------------------

	def _printClearedPositions(self):
		"""Print all bottles that have had their positions cleared. This
		indicates the bottle is no longer stored in any particular location of
		the cellar. Such bottles are likely errors in the placement algorihms,
		so this output is highlighted in red.
		"""

		n = 0
		for bottle in self._bottlePositions:
			if bottle.boldness_coord == None and bottle.price_coord == None and bottle.hold_coord == None:
				n += 1
				print("%s %s" % (
					stylize(Fore.RED, "Clear position for"),
					stylize(Style.BRIGHT, bottle.label.description)))

		return n

	def _printChangedPositions(self):
		"""Print all bottles that have had their positions changed."""

		n = 0
		for bottle in self._bottlePositions:
			if bottle.boldness_coord != None or bottle.price_coord != None or bottle.hold_coord != None:
				n += 1
				print("%s %s %s" % (
					stylize(Fore.BLUE, "Move"),
					stylize(Style.BRIGHT, bottle.label.description),
					stylize(Fore.BLUE, "to (%d, %d, %d)" % (
						bottle.boldness_coord,
						bottle.price_coord,
						bottle.hold_coord))))

		return n
