#!/usr/bin/env python3

# This script shows the contents of the cellar, organized positionally. It can
# be used to see where the various bottles should be placed.

# --------------------------------------------------------------------------------

import os
import math

from colorama import Fore, Back, Style

from backend.raw import db
from backend.cellar import Cellar
from scripts.confirm import confirmAndCommit

cellar = Cellar()
layout = cellar.computeLayout()

# Expand out the bins into real thresholds
def expandBins(bins):
	expanded = []
	for threshold, width in bins:
		for i in range(0, width):
			expanded.append(threshold)

	return expanded

boldnessThresholds = expandBins(layout.boldBins)
costThresholds = expandBins(layout.costBins)
holdThresholds = expandBins(layout.holdBins)

boldnessThresholds.reverse()

rows = len(costThresholds) * (len(holdThresholds) + 1)
cols = len(boldnessThresholds) + 2
outputTable = [["" for c in range(0, cols)] for r in range(0, rows)]
outputStyle = [["" for c in range(0, cols)] for r in range(0, rows)]

outputTable[0][0] = "Cost"
outputTable[0][1] = "Hold"

outputStyle[0][0] = Style.BRIGHT
outputStyle[0][1] = Style.BRIGHT

# Label the Holds, with special cases for first entry and infinity
holdLabels = ['Hold < %d' % h if h != math.inf else 'Hold Longer' for h in holdThresholds]
holdLabels[0] = "Drink Now"

# Label the Boldness
boldnessLabels = ['Boldness < %d' % b if b != math.inf else 'Bolder' for b in boldnessThresholds]
for idx, label in enumerate(boldnessLabels):
	outputTable[0][idx + 2] = label
	outputStyle[0][idx + 2] = Style.BRIGHT

# Label the Costs
costLabels = ['< $%.0f' % c if c != math.inf else '$ more' for c in costThresholds]
for idx, label in enumerate(costLabels):
	outputTable[(len(costThresholds) - idx - 1) * (len(holdThresholds) + 1) + 1][0] = label
	outputStyle[(len(costThresholds) - idx - 1) * (len(holdThresholds) + 1) + 1][0] = Fore.GREEN

	for hidx, hlabel in enumerate(holdLabels):
		outputTable[idx * (len(holdThresholds) + 1) + len(holdThresholds) - hidx][1] = hlabel
		outputStyle[idx * (len(holdThresholds) + 1) + len(holdThresholds) - hidx][1] = Fore.BLUE

# Add the Bottles
for b in range(0, len(boldnessThresholds)):
	for c in range(0, len(costThresholds)):
		for h in range(0, len(holdThresholds)):
			rowCoord = (len(costThresholds) - c - 1) * (len(holdThresholds) + 1) + len(holdThresholds) - h
			colCoord = b + 2

			outputTable[rowCoord][colCoord] = "        --------"

for bottle in layout.bottles:
	coord = bottle.coordinate
	if coord is not None:
		(b, c, h) = coord
		rowCoord = (len(costThresholds) - c - 1) * (len(holdThresholds) + 1) + len(holdThresholds) - h
		colCoord = b + 2

		outputTable[rowCoord][colCoord] = bottle.label.description

# ----------------------------------------
# Print the table

widths = []
for c in range(0, cols):
	lengths = [ len(outputTable[r][c]) for r in range(0, rows) ]
	widths.append(max(lengths))

def printCell(r, c):
	print(" %s|%s %s%-*s%s" % (
		    Fore.BLUE, Style.RESET_ALL,
		    outputStyle[r][c], widths[c], outputTable[r][c], Style.RESET_ALL),
	      end='')

def printSomeColumns(colRange):
	for r in range(0, rows):
		printCell(r, 0)
		printCell(r, 1)

		for c in colRange:
			printCell(r, c)

		print()

colStart = 2
colEnd = 2
lineWidth = int(os.popen('stty size', 'r').read().split()[1])
availableWidth = lineWidth - sum(widths[0:2]) - (2 * 3)

while colStart < cols:
	while colEnd < cols - 1 and (sum(widths[colStart:colEnd + 2]) + (colEnd - colStart + 2) * 3) < availableWidth:
		colEnd += 1

	if (colStart > 2):
		print()
		print(Fore.BLUE, '-' * (lineWidth - 2), Style.RESET_ALL)
		print()

	printSomeColumns(range(colStart, colEnd + 1))

	colStart = colEnd + 1
	colEnd = colStart
