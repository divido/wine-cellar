#!/usr/bin/env python3

from . import db

# --------------------------------------------------------------------------------

def MakeParentChild(parentClass, childClass):
	"""Establishes a parent-child relationship between the two table classes
	listed. The child will add a database column, named based on the parent's
	singular form, as well as a relationship back reference for programmatic
	access. The parent gets a plural form relationship.
	"""

	setattr(childClass, parentClass._singular + '_id',
			db.Column(db.Integer, db.ForeignKey(parentClass.__tablename__ + '.id')))

	setattr(parentClass, childClass._plural,
			db.relationship(childClass, backref=parentClass._singular, lazy='immediate'))

# --------------------

class TableBase(db.Model):
	"""Define the base functionality for the tables, including a simple primary
	key. This class is mostly reserved for future use
	"""

	__abstract__ = True

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
