#!/usr/bin/env python3

from .raw.data_model import Label, Bottle
from .raw import db

from sqlalchemy.sql import func

# --------------------------------------------------------------------------------

class Cellar:
	"""This is the main organizer class. It manages operations that run on
	bottles currently in possession (stored in the cellar).
	"""

	@property
	def labels(self):
		"""The returns all wine labels that currently have at least one bottle
		in the cellar.
		"""

		q = db.session.query(Label).join(Bottle).filter(Bottle.consumption == None)
		return [label for label in q.all()]
