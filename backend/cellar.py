#!/usr/bin/env python3

from .raw.data_model import Label, Bottle
from .raw import db
from .databaseLogger import DatabaseLogger
from .dividoLayout import DividoLayout

from sqlalchemy.sql import func
from datetime import date

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
			first.year: {n: 0 for n in range(first.month, 13)},
			currentYear: {n: 0 for n in range(1, currentMonth + 1)}
		}

		q = db.session.query(Bottle).filter(Bottle.consumption != None)
		for bottle in q.all():
			year = bottle.consumption.year
			month = bottle.consumption.month

			if year not in consumption:
				consumption[year] = {n: 0 for n in range(1, 13)}

			consumption[year][month] += 1

		return consumption

	def consumptionProjection(self):
		"""This computes a projection of the cellar bottles over time. The
		resulting dictionary object contains an entry for the average annual
		consumption, the total bottle count, and the number to be consumed each
		year (including excess / shortage amounts). This is useful for
		visualizing the cellar contents over time.
		"""

		q = db.session.query(
			func.count(Bottle.consumption),
			func.max(Bottle.consumption),
			func.min(Bottle.consumption))
		totalConsumption, mostRecent, first = q.one()
		numYears = (mostRecent - first).days / 365;

		averageAnnualConsumption = totalConsumption / numYears
		totalBottleCount = 0

		currentYear = date.today().year
		aggregated = {}

		# Little helper, notably fills in gaps with an entry (without extrapolating)
		def createYears(year):
			for yr in range(currentYear, year + 1):
				if yr not in aggregated:
					aggregated[yr] = { 'count': 0 }

		createYears(currentYear)

		for label in self.labels:
			inventoryByYear = label.inventoryByYear()
			for holdYear, holdAmt in inventoryByYear.items():
				createYears(holdYear)
				aggregated[holdYear]['count'] += holdAmt
				totalBottleCount += holdAmt

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
			'totalBottleCount': totalBottleCount,
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

		q = db.session.query(Bottle).filter(Bottle.consumption == None)
		for bottle in q.all():
			region = bottle.label.winery.region
			country = region.country

			if country not in regionBottles:
				regionBottles[country] = {}
				countryBottles[country] = []

			if region not in regionBottles[country]:
				regionBottles[country][region] = []

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
