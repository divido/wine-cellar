from datetime import date
from sortedcontainers import SortedList
import math

NumBoldLevels = 12 # 12 stacks, not counting last (save for whites / other's wine / etc.)
NumCostLevels = 12 # 12 different heights
NumHoldLevels = 3  # 3 depths, note that first is only for holdYear <= currentYear

# --------------------------------------------------------------------------------

class BottleStack:
	"""This class represents a single vertical stack of bottles, which means
	they all have the same hold coordinate and boldness coordinate. It manages
	the sorting of the bottles within to keep the price coordinates as accurate
	as possible and like-bottles together.
	"""

	def __init__(self, boldnessCoords, holdCoord):
		"""Build the stack, positioned at the supplied coordinates. It is
		possible for one "stack" to span multiple (physical) boldness
		coordinates, if enough bottles have the same boldness score to merit
		multiple stacks. In these cases, the bottles will be balanced between
		all boldness values evenly.
		"""

		self.positioned = []
		self.unpositioned = SortedList()
		self.width = len(boldnessCoords)
		self.boldnessCoords = boldnessCoords
		self.holdCoord = holdCoord

	def addPositioned(self, bottle):
		"""Add a bottle to the stack that is already positioned (and therefore
		should not be moved during a positionBottles() call).
		"""

		self.positioned.append(bottle)

	def addUnpositioned(self, bottle):
		"""Add a bottle to the stack that does not have a current position, or
		should be re-positioned as part of a positionBottles() call.
		"""

		self.unpositioned.add(bottle)

	def openSlotsAtOrAbove(self, costCoord):
		"""This counts the number of open slots available within the stack at or
		above the specified cost coordinate. This takes into account all
		positioned bottles.
		"""

		available = (NumCostLevels - costCoord) * self.width
		used = 0
		for bottle in self.positioned:
			if bottle.price_coord >= costCoord: used += 1

		return available - used

	def positionBottles(self, logger, costBins):
		"""This causes all unpositioned bottles to be given positions within the
		stack. The supplied cost bins are used to guide the placement of the
		bottles. Generally speaking, bottles will be placed in their
		corresponding bin, with duplicate entries taking higher cost
		slots. However, if there is not enough space above, the bottles are
		moved down instead. At the outset, if there are not enough slots for the
		bottles, an exception is raised.
		"""

		if self.openSlotsAtOrAbove(0) < len(self.unpositioned):
			raise RuntimeError('Not enough open slots for all unpositioned bottles.')

		# Maintaining the number of slots above is important to know if we need
        # to start putting bottles in cheaper slots just to fit. Keeping the
        # at-or-above lets us compute the space at the level.
		costCoord = 0
		openAtOrAbove = self.openSlotsAtOrAbove(costCoord)
		openAbove = self.openSlotsAtOrAbove(costCoord + 1)

		while len(self.unpositioned) > 0:
			notEnoughRoomAbove = (openAbove < len(self.unpositioned))
			costMeetsBin = (self.unpositioned[0].cost < costBins[costCoord][0])
			roomAtThisLevel = (openAtOrAbove - openAbove > 0)

			if roomAtThisLevel and (notEnoughRoomAbove or costMeetsBin):
				self._placeFirstBottle(logger, costCoord)
				openAtOrAbove -= 1

			else:
				# Once we no longer want to place bottle here, move up. Note
                # that the computation of the at-or-above is fairly simple since
                # we already know "above" and are moving up :)
				costCoord += 1
				openAtOrAbove = openAbove
				openAbove = self.openSlotsAtOrAbove(costCoord + 1)

	# ----------------------------------------

	def _placeFirstBottle(self, logger, costCoord):
		"""This places the bottom-most bottle of the unpositioned bottles. They
		are always sorted by price, so this will be the cheapest of the
		bottles. Thus, whenever we get a slot, we put this first bottle
		there. The cost coordinate is supplied, but the boldness coordinate is
		computed to be whichever column has the least bottles thus far.
		"""

		boldCoordUsage = [0 for b in self.boldnessCoords]
		for bottle in self.positioned:
			boldCoordUsage[self.boldnessCoords.index(bottle.boldness_coord)] += 1

		leastUsed = 0
		for idx in range(1, len(boldCoordUsage)):
			if boldCoordUsage[idx] < boldCoordUsage[leastUsed]:
				leastUsed = idx

		bottle = self.unpositioned[0]

		bottle.boldness_coord = self.boldnessCoords[leastUsed]
		bottle.price_coord = costCoord
		bottle.hold_coord = self.holdCoord
		logger.changedBottlePosition(bottle)

		self.unpositioned.remove(bottle)
		self.positioned.append(bottle)

# --------------------------------------------------------------------------------

class DividoLayout:
	"""This represents the layout engine for a standard Divido cellar. Which is
	to say, generic algorithms are hard, easier to hard-code to my specific
	desires.
	"""

	def __init__(self, bottles):
		"""Builds a cellar and populates it with the supplied bottles"""

		currentYear = date.today().year

		self.bottles = bottles

		self.boldBins = self._createBins([
			bottle.label.weightedBoldness for bottle in bottles
		], NumBoldLevels, True)

		self.costBins = self._createBins([
			bottle.cost for bottle in bottles
		], NumCostLevels, False)

		# Note we force the first bin to "< currentYear + " (aka "<= currentYear")
		self.holdBins = self._createBins([
			bottle.hold_until for bottle in bottles if bottle.hold_until > currentYear
		], NumHoldLevels - 1, False)
		self.holdBins.insert(0, (currentYear + 1, 1))

		self.stacks = []
		for boldIdx in range(0, len(self.boldBins)):
			boldnessCoords = self._boldnessCoordsForBin(boldIdx)
			self.stacks.append([])

			for holdIdx in range(0, len(self.holdBins)):
				self.stacks[boldIdx].append(BottleStack(boldnessCoords, holdIdx))

		# --------------------

		for bottle in bottles:
			if bottle.coordinate is not None:
				boldBin = self._boldnessBinIdx(bottle.boldness_coord)
				self.stacks[boldBin][bottle.hold_coord].addPositioned(bottle)

			else:
				boldBin = self._findBin(bottle.label.weightedBoldness, self.boldBins)
				holdBin = self._findBin(bottle.hold_until, self.holdBins)
				self.stacks[boldBin][holdBin].addUnpositioned(bottle)

	# ----------------------------------------

	def positionBottles(self, logger):
		"""Position the bottles within the stacks. The BottleStack objects do
		most of the work, this basically just iterates over them and provides a
		consistent set of cost bins.
		"""

		for holdStacks in self.stacks:
			for stack in holdStacks:
				stack.positionBottles(logger, self.costBins)

	# ----------------------------------------

	def _createBins(self, data, numBins, allowMultiple):
		"""This helper computes the bin boundaries that more or less evenly
		spreads the supplied data points. If allowMultiple is true, then
		clustered data will cause multiple bins to have the same
		boundaries. That condition is represented by returning less bins than
		requested, but with the width value (the second value of the pairs)
		greater than 1.
		"""

		remainingData = data[:]
		remainingData.sort()

		desiredPerBin = math.floor(len(data) / numBins)
		desired = desiredPerBin

		thresholds = []
		threshold = math.floor(remainingData[0])
		included = 0

		binsToGo = numBins - 1

		while binsToGo > 0:
			while len(remainingData) > 0 and remainingData[0] < threshold:
				remainingData.pop(0)
				included += 1

			if included >= desired or len(remainingData) == 0:
				binWidth = 0
				while included >= desired and binsToGo - binWidth > 0:
					binWidth += 1
					desired += desiredPerBin
					if not allowMultiple: break

				thresholds.append((threshold, binWidth))
				binsToGo -= binWidth

			threshold += 1

		# The very last is always "< math.inf" to pick up the stragglers
		thresholds.append((math.inf, 1))
		return thresholds

	# ----------------------------------------

	def _boldnessBinIdx(self, boldCoord):
		"""This computes the boldness bin index from the supplied
		coordinate. This covers two aspects, firstly that bins can be wider than
		a single stack; and secondly than boldness coordinates are reversed from
		bins (coordinates get less bold as they increase, while bins get bolder
		when increasing).
		"""

		idx = 0
		covers = 0
		for boldThreshold, boldWidth in self.boldBins:
			covers += boldWidth
			if (NumBoldLevels - boldCoord - 1) < covers: break
			idx += 1

		return idx

	def _boldnessCoordsForBin(self, binIdx):
		"""This reverses _boldnessBinIdx, but returns an array of all
		coordinates that would have mapped to the supplied bin.
		"""

		idx = 0
		covers = 0
		for boldThreshold, boldWidth in self.boldBins:
			if idx == binIdx:
				return [NumBoldLevels - c - 1 for c in range(covers, covers + boldWidth)]

			covers += boldWidth
			idx += 1

		return [NumBoldLevels - covers - 1]

	def _findBin(self, attribute, bins):
		"""This finds which bin the bottle should be placed in ideally, based on
		the supplied attribute.
		"""

		for idx in range(0, len(bins) - 1):
			if attribute < bins[idx][0]:
				return idx

		return len(bins) - 1
