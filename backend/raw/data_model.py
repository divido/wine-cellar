#!/usr/bin/env python3

from . import db
from .table_base import TableBase, MakeParentChild

from datetime import date

# --------------------------------------------------------------------------------

class Region(TableBase):
	"""This represents a single wine producing region. It is separated into a
	Region name and a Country of origin.
	"""

	_singular = 'region'
	_plural = 'regions'
	__tablename__ = _plural

	name = db.Column(db.Text)
	country = db.Column(db.Text)

	@property
	def description(self):
		"""This returns a compact description of the region, suitable for human
		consumption.
		"""
		return "%s, %s" % (self.name, self.country)

	def inventoryByYear(self):
		"""This computes the number of bottles of from this region that are
		owned (i.e., not consumed). The results are grouped by hold year and
		returned as a dictionary, with the keys of the dictionaries being the
		year and the values being the counts. All hold years earlier than the
		current year will be considered to be the current year (i.e., "Drink
		Now"). This effectively sums the inventoryByYear results from all labels
		from wineries within this region.
		"""

		currentYear = date.today().year
		inventory = {}

		for winery in self.wineries:
			for label in winery.labels:
				labelByYear = label.inventoryByYear()

				for holdYear in labelByYear:
					if holdYear not in inventory:
						inventory[holdYear] = labelByYear[holdYear]

					else:
						inventory[holdYear] += labelByYear[holdYear]

		return inventory

# ----------------------------------------

class Winery(TableBase):
	"""This represents a single winery / vintner. It is mostly used for grouping
	together various wine labels.
	"""

	_singular = 'winery'
	_plural = 'wineries'
	__tablename__ = _plural

	name = db.Column(db.Text)

MakeParentChild(Region, Winery)

# ----------------------------------------

class Label(TableBase):
	"""This represents a particular kind of wine, of a certain vintage, from a
	particular winery. The database of labels will grow over time, and contains
	all bottle types ever owned. This stores the fundamental attributes of the
	wine that do not vary from bottle to bottle.
	"""

	_singular = 'label'
	_plural = 'labels'
	__tablename__ = _plural

	name = db.Column(db.Text)
	vintage = db.Column(db.Integer)
	abv = db.Column(db.Float)

	@property
	def description(self):
		"""This returns a compact description of the bottom, including the name
		of the winery that produces it. This description is suitable to be used
		as the primary name of the wine, from a human's persepective.
		"""

		return "%d %s %s" % (self.vintage, self.winery.name, self.name)

	@property
	def varietalDescription(self):
		"""This returns a list of the varietals in the wine, including the blend
		portions (percentages). If there is only a single varietal, then that is
		returned directly (the 100% is assumed). Otherwise, a comma separated
		list of portions is returned, sorted so the most prominent varietal
		shows up first.
		"""
		if len(self.blends) == 1:
			return self.blends[0].varietal.name

		blendPortions = ['%d%% %s' % (blend.portion, blend.varietal.name)
		                 for blend in sorted(self.blends, key=lambda b: b.portion, reverse=True)]

		return '(' + ', '.join(blendPortions) + ')'

	@property
	def weightedBoldness(self):
		"""This returns the effective boldness score of the label, based on the
		blend. Each varietal within the blend has a boldness score, these are
		weighted based on the portion of the wine made up by that varietal.
		"""

		return sum([blend.varietal.boldness * blend.portion / 100.0 for blend in self.blends])

	def inventoryByYear(self):
		"""This computes the number of bottles of this label that are owned
		(i.e., not consumed). The results are grouped by hold year and returned
		as a dictionary, with the keys of the dictionaries being the year and
		the values being the counts. All hold years earlier than the current
		year will be considered to be the current year (i.e., "Drink Now").
		"""

		currentYear = date.today().year
		inventory = {}

		for bottle in self.bottles:
			if bottle.consumption == None:
				holdYear = max(currentYear, bottle.hold_until)
				if holdYear not in inventory:
					inventory[holdYear] = 1

				else:
					inventory[holdYear] += 1

		return inventory

MakeParentChild(Winery, Label)

# ----------------------------------------

class Varietal(TableBase):
	"""This represents a particular varietal of wine. It is used to maintain
	consistent boldness scoring across labels.
	"""

	_singular = 'varietal'
	_plural = 'varietals'
	__tablename__ = _plural

	name = db.Column(db.Text)
	boldness = db.Column(db.Integer)

# ----------------------------------------

class Blend(TableBase):
	"""This represents a pairing of the varietals to the wine labels. Each wine
	label can contain any number of Blend objects, each of wine pairs a specific
	varietal to a portion (represented as a percentage, integer 1-100). For any
	given label, the total of the blend portions should add to exactly 100, but
	this is not enforced by the data model.
	"""

	_singular = 'blend'
	_plural = 'blends'
	__tablename__ = _plural

	portion = db.Column(db.Integer)

MakeParentChild(Label, Blend)
MakeParentChild(Varietal, Blend)

# ----------------------------------------

class Bottle(TableBase):
	"""This represents a physical bottle, as a real-world instance of a wine
	label. It keeps track of acquisition / consumption dates, prices, and cellar
	coordinates.
	"""

	_singular = 'bottle'
	_plural = 'bottles'
	__tablename__ = _plural

	cost = db.Column(db.Float)

	acquisition = db.Column(db.Date)
	consumption = db.Column(db.Date)
	hold_until = db.Column(db.Integer)

	boldness_coord = db.Column(db.Integer)
	price_coord = db.Column(db.Integer)
	hold_coord = db.Column(db.Integer)

	@property
	def coordinate(self):
		"""This returns a simple triplet of the bottle's coordinates"""
		if self.boldness_coord is None and self.price_coord is None and self.hold_coord is None:
			return None

		return (self.boldness_coord, self.price_coord, self.hold_coord)

	def __lt__(self, other):
		"""This comparator sorts bottles by cost, keeping like-bottles together"""
		selfAttrs = (self.cost, self.label.winery.name, self.label.name, self.label.vintage)
		otherAttrs = (other.cost, other.label.winery.name, other.label.name, other.label.vintage)
		return selfAttrs < otherAttrs

MakeParentChild(Label, Bottle)
