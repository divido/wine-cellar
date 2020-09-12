#!/usr/bin/env python3

from .raw.data_model import Region, Winery, Label, Varietal, Blend, Bottle
from .raw import db
from .databaseLogger import DatabaseLogger

# --------------------------------------------------------------------------------

class Repository:
	"""This maintains access to every part of the database. It is primarily used
	to retrieve listings of all wineries, labels, etc.
	"""

	logger = DatabaseLogger()

	@property
	def regions(self):
		"""The returns all regions in the database"""

		q = db.session.query(Region)
		return q.all()

	@property
	def wineries(self):
		"""The returns all wineries in the database"""

		q = db.session.query(Winery)
		return q.all()

	@property
	def varietals(self):
		"""The returns all varietals in the database"""

		q = db.session.query(Varietal)
		return q.all()

	def findLabel(self, winery, labelName, vintage):
		"""The searches for a label from the supplied winery in the given
		vintage, or None if not found.
		"""

		q = db.session.query(Label) \
		              .filter(Label.winery == winery) \
		              .filter(Label.name == labelName) \
		              .filter(Label.vintage == vintage)

		matching = q.all()
		if len(matching) == 0:
			return None

		return matching[0]

	# ----------------------------------------

	def addRegion(self, name, country):
		"""Add a new region to the database"""

		region = Region(name=name, country=country)
		db.session.add(region)
		self.logger.newRegion(region)
		return region

	def addWinery(self, name, region):
		"""Add a new winery to the database"""

		winery = Winery(name=name, region=region)
		db.session.add(winery)
		self.logger.newWinery(winery)
		return winery

	def addLabel(self, name, vintage, abv, winery, varietalPortions):
		"""Add a new wine label to the database"""

		label = Label(name=name, vintage=vintage, abv=abv, winery=winery)
		db.session.add(label)
		self.logger.newLabel(label)

		for varietal, portion in varietalPortions:
			blend = Blend(portion=portion)
			db.session.add(blend)

			varietal.blends.append(blend)
			label.blends.append(blend)

		return label

	def addVarietal(self, name, boldness):
		"""Add a new varietal to the database"""

		varietal = Varietal(name=name, boldness=boldness)
		db.session.add(varietal)
		self.logger.newVarietal(varietal)
		return varietal

	def addBottle(self, cost, acquisition, hold_until, label):
		"""Add a new bottle to the database"""

		bottle = Bottle(cost=cost, acquisition=acquisition, hold_until=hold_until, label=label)
		db.session.add(bottle)
		self.logger.newBottle(bottle)
		return bottle

	def changeLabelWinery(self, label, winery):
		"""Change the winery a label belongs to. This is expected to be used
		when fracturing a winery into multiple regions.
		"""

		label.winery = winery
		self.logger.changedLabelWinery(label)
