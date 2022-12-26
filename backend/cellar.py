#!/usr/bin/env python3

from .raw.data_model import Label, Bottle, Region, Varietal
from .raw import db
from .databaseLogger import DatabaseLogger
from .dividoLayout import DividoLayout

from sqlalchemy.sql import func
from datetime import date

import math

# --------------------------------------------------------------------------------

class Cellar:
	"""This is the main organizer class. It manages operations that run on
	bottles currently in possession (stored in the cellar).
	"""

	logger = DatabaseLogger()

	@property
	def labels(self):
		"""The returns all wine labels that currently have at least one bottle
		in the cellar.
		"""

		q = db.session.query(Label).join(Bottle).filter(Bottle.consumption == None)
		return q.all()

	@property
	def bottles(self):
		"""The returns all bottles in the cellar"""

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		return q.all()

	@property
	def bottlesByYear(self):
		"""This returns all bottles in the cellar that are owned (i.e., not
		consumed). The results are grouped by hold year and returned as a
		dictionary, with the keys of the dictionaries being the year and the
		values being an array of bottles. All hold years earlier than the
		current year will be considered to be the current year (i.e., "Drink
		Now").  """

		currentYear = date.today().year
		inventory = {}

		for bottle in self.bottles:
			holdYear = max(currentYear, bottle.hold_until)
			if holdYear not in inventory:
				inventory[holdYear] = []

			inventory[holdYear].append(bottle)

		return inventory

	@property
	def bottlesPastHold(self):
		"""This returns all bottles in the cellar that are not consumed and have
		a hold year in the past."""

		currentYear = date.today().year
		pastHold = []

		for bottle in self.bottles:
			if bottle.hold_until < currentYear:
				pastHold.append(bottle)

		return pastHold

	# --------------------------------------------------------------------------------

	def consumptionByMonth(self):
		"""This computes a count of bottle consumption to date. The returned
		object is indexed first by year, then by month, and returns a count of
		consumed bottles. Months are 1-based
		"""

		q = db.session.query(func.min(Bottle.consumption))
		first = q.one()[0]

		currentYear = date.today().year
		currentMonth = date.today().month
		consumption = {
			first.year: {n: [] for n in range(first.month, 13)},
			currentYear: {n: [] for n in range(1, currentMonth + 1)}
		}

		q = db.session.query(Bottle).filter(Bottle.consumption != None).order_by(Bottle.consumption)
		for bottle in q.all():
			year = bottle.consumption.year
			month = bottle.consumption.month

			if year not in consumption:
				consumption[year] = {n: [] for n in range(1, 13)}

			consumption[year][month].append(bottle)

		return consumption

	def consumptionProjection(self):
		"""This computes a projection of the cellar bottles over time. The
		resulting dictionary object contains an entry for the average annual
		consumption, the averaged consumed bottle's cost, the total stored
		bottle count / value, and the number to be consumed each year (including
		excess / shortage amounts). This is useful for visualizing the cellar
		contents over time.
		"""

		q = db.session.query(
			func.count(Bottle.consumption),
			func.min(Bottle.consumption))
		numConsumed, first = q.one()

		now = date.today()
		numYears = (now - first).days / 365

		averageAnnualConsumption = numConsumed / numYears
		numStored = 0
		valueStored = 0
		totalValue = 0

		currentYear = now.year
		aggregated = {}

		# Little helper, notably fills in gaps with an entry (without extrapolating)
		def createYears(year):
			for yr in range(currentYear, year + 1):
				if yr not in aggregated:
					aggregated[yr] = { 'count': 0 }

		createYears(currentYear)

		q = db.session.query(Bottle)
		for bottle in q:
			if bottle.consumption is None:
				valueStored += bottle.inflatedCost
				numStored += 1
				holdYear = max(currentYear, bottle.hold_until)
				createYears(holdYear)
				aggregated[holdYear]['count'] += 1

			totalValue += bottle.inflatedCost

		carryover = 0
		for holdYear in aggregated:
			consumption = averageAnnualConsumption
			if holdYear == currentYear:
				daysLeft = (date(currentYear + 1, 1, 1) - date.today()).days
				consumption = round(averageAnnualConsumption * daysLeft / 365)

			aggregated[holdYear]['excess'] = (aggregated[holdYear]['count'] + carryover - consumption)
			carryover = max(0, aggregated[holdYear]['excess'])

		return {
			'averageAnnualConsumption': averageAnnualConsumption,
			'averageConsumedBottleValue': (totalValue - valueStored) / numConsumed,

			'numStored': numStored,
			'valueStored': valueStored,

			'byYear': aggregated
		}

	def byRegion(self):
		"""This returns a list of all bottles in the cellar, organized by
		region. The returned list contains data for each country in descending
		order of bottle counts. Each country object contains a similar array of
		regions.
		"""

		regionBottles = {}
		countryBottles = {}

		q = db.session.query(Region)
		for region in q.all():
			country = region.country
			if country not in regionBottles:
				regionBottles[country] = {}
				countryBottles[country] = []

			regionBottles[country][region] = []
			countryBottles[country] = []

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		for bottle in q.all():
			region = bottle.label.winery.region
			country = region.country

			regionBottles[country][region].append(bottle)
			countryBottles[country].append(bottle)

		return [{
			'country': country,
			'bottles': countryBottles[country],
			'regions': [{
				'region': region,
				'bottles': regionBottles[country][region]
			} for region in sorted(regionBottles[country], key=lambda r: len(regionBottles[country][r]), reverse=True)]
		} for country in sorted(countryBottles, key=lambda c: len(countryBottles[c]), reverse=True)]

	def byVarietal(self):
		"""This returns a count of each varietal, separated into several
		different "buckets" by boldness. Each bucket contains the list of
		varietals, and their respective bottle counts, separated into "pure"
		(bottles that are 100% that varietal) and "blend" (the summated portions
		across all non-pure bottles). The blendCount does not given any
		information about how many physical bottles contain the varietal, but
		gives a sense of how much of the varietal is featured in the cellar.
		"""

		numBuckets = 6
		bucketWidth = 12

		varietalBuckets = [[] for i in range(0, numBuckets)]

		# --------------------

		totalCount = {}
		pureCountByYear = {}
		blendCountByYear = {}

		q = db.session.query(Varietal)
		for varietal in q.all():
			totalCount[varietal] = 0
			pureCountByYear[varietal] = {}
			blendCountByYear[varietal] = {}
			bucketIndex = min(numBuckets - 1, math.floor(varietal.boldness / bucketWidth))

			varietalBuckets[bucketIndex].append(varietal)

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		for bottle in q.all():
			for blend in bottle.label.blends:
				totalCount[blend.varietal] += blend.portion / 100

				if bottle.hold_until not in pureCountByYear[blend.varietal]:
					pureCountByYear[blend.varietal][bottle.hold_until] = 0
					blendCountByYear[blend.varietal][bottle.hold_until] = 0

				if blend.portion == 100:
					pureCountByYear[blend.varietal][bottle.hold_until] += 1
				else:
					blendCountByYear[blend.varietal][bottle.hold_until] += blend.portion / 100

		return [{
			'bucketName': 'Boldness ' + (
				'<= ' + str(bucketWidth) if i == 0 else
				'>= ' + str(bucketWidth * (numBuckets - 1) + 1) if i == numBuckets - 1 else
				str(bucketWidth * i + 1) + ' to ' + str(bucketWidth * (i + 1))),
			'data': [{
				'varietal': varietal,
				'totalCount': totalCount[varietal],
				'pureCountByYear': pureCountByYear[varietal],
				'blendCountByYear': blendCountByYear[varietal]
			} for varietal in sorted(varietalBuckets[i], key=lambda v: totalCount[v], reverse=True)]
		} for i in reversed(range(0, numBuckets))]

	# --------------------------------------------------------------------------------

	def consume(self, bottle, consumption):
		"""This marks a bottle as consumed on the supplied date"""
		bottle.consumption = consumption
		self.logger.consumedBottle(bottle)

	# --------------------------------------------------------------------------------

	def clearBottlePositions(self):
		"""This removes all bottles from the cellar, leaving them in an
		unpositioned state. This is generally useful before repositioning them
		to perform a full defragmentation operation.
		"""

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		for bottle in q.all():
			bottle.boldness_coord = None
			bottle.price_coord = None
			bottle.hold_coord = None
			self.logger.changedBottlePosition(bottle)

	def computeLayout(self):
		"""This constructs a DividoLayout for the cellar, adding the bottles
		that we know about. With this object, bottles can be repositioned or
		placed new.
		"""

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		return DividoLayout(q.all())
