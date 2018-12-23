#!/usr/bin/env python3

import sys
sys.stderr = open('/tmp/wine-service-stderr.txt', 'w')

import logging
logging.basicConfig(filename='/tmp/wine-service.log', level=logging.DEBUG, filemode='w')

from flask import jsonify

from flipflop import WSGIServer
from backend.raw import app
from backend.cellar import Cellar

cellar = Cellar()

# --------------------------------------------------------------------------------

@app.route("/inventory")
def inventory():
	"""This endpoint returns data about the labels associated to bottles in the
	cellar. This provides the same data as is used by the inventory script.
	"""

	result = []

	for label in sorted(cellar.labels, key=lambda l: l.weightedBoldness, reverse=True):
		labelObject = label.value
		labelObject.update({
			'description': label.description,
			'varietalDescription': label.varietalDescription,
			'regionDescription': label.winery.region.description
		})

		result.append(labelObject)

	return jsonify(result)

# --------------------------------------------------------------------------------

if __name__ == '__main__':
	logging.info('Starting up the wine service')
	WSGIServer(app).run()
