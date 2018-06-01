#!/usr/bin/env python3

from datetime import date
import math

currentYear = date.today().year
NumCostLevels = 12 # 12 different heights
NumBoldLevels = 12 # 12 stacks, not counting last (save for whites / other's wine / etc.)
NumHoldLevels = 3  # 3 depths, note that first is only for holdYear <= currentYear

def _createBins(data, numBins):
	remainingData = data[:]
	remainingData.sort()

	desiredPerBin = math.floor(len(data) / numBins)
	desired = desiredPerBin

	thresholds = []
	threshold = math.floor(remainingData[0])
	included = 0

	while len(thresholds) + 1 < numBins:
		while len(remainingData) > 0 and remainingData[0] < threshold:
			remainingData.pop(0)
			included += 1

		if included >= desired or len(remainingData) == 0:
			thresholds.append(threshold)
			desired += desiredPerBin

		threshold += 1

	thresholds.append(math.inf)
	return thresholds

def buildLayout(allCosts, allBoldness, allHold):
	layout = {
		'costThresholds': _createBins(allCosts, NumCostLevels),
		'boldnessThresholds': _createBins([-b for b in allBoldness], NumBoldLevels),
		'holdThresholds': _createBins(allHold, NumHoldLevels - 1),
		'bottles': [
			[
				[None for h in range(NumHoldLevels)]
				for c in range(NumCostLevels)
			] for b in range(NumBoldLevels)
		]
	}

	return layout

def computeIdealCoord(layout, bottle):
	boldCoord = 0
	costCoord = 0
	holdCoord = 0

	for idx, thresh in enumerate(layout['boldnessThresholds']):
		if (-bottle['boldness'] < thresh):
			boldCoord = idx
			break

	for idx, thresh in enumerate(layout['costThresholds']):
		if (bottle['cost'] < thresh):
			costCoord = idx
			break

	if bottle['holdUntil'] > currentYear:
		for idx, thresh in enumerate(layout['holdThresholds']):
			if (bottle['holdUntil'] < thresh):
				holdCoord = idx + 1
				break

	return (boldCoord, costCoord, holdCoord)

def addBottle(layout, bottle, recurse=False):
	ideal = computeIdealCoord(layout, bottle)
	holdRange = range(0, 1) if bottle['holdUntil'] <= currentYear else range(1, NumHoldLevels)

	best = {
		'dist': math.inf,
		'displacedDist': -math.inf
	}

	for h in holdRange:
		for c in range(0, NumCostLevels):
			for b in range(0, NumBoldLevels):
				current = layout['bottles'][b][c][h]

				# Scale distance to prefer movement in hold or cost over boldness
				dist = (abs(b - ideal[0]) * 5 +
				        abs(c - ideal[1]) * 2 +
				        abs(h - ideal[2]))
				displacedDist = -math.inf

				if current is not None:
					displacedDist = current['dist']

				betterDist = (dist < best['dist'])
				betterDisplace = (displacedDist < best['displacedDist'])

				# Only kick out bottles that have lower distance than us
				# Also, search for the lowest distance for us, or lowest bottle to be displaced if equivalent distances
				if displacedDist < dist and (betterDist or (dist == best['dist'] and betterDisplace)):
					best = {
						'coord': (b, c, h),
						'dist': dist,
						'displacedDist': displacedDist
					}

	boldCoord = best['coord'][0]
	costCoord = best['coord'][1]
	holdCoord = best['coord'][2]
	bottle['coord'] = best['coord']
	bottle['dist'] = best['dist']

	current = layout['bottles'][boldCoord][costCoord][holdCoord]
	layout['bottles'][boldCoord][costCoord][holdCoord] = bottle

	if current is not None:
		addBottle(layout, current, True)
