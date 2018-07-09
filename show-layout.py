#!/usr/bin/env python3

import os
from colorama import Fore, Back, Style
from datetime import date

from bottlePlacement import buildLayout, addExistingBottle, NumCostLevels, NumBoldLevels, NumHoldLevels

import sqlite3

db = sqlite3.connect('cellar.db')
sql = db.cursor()

labelData = sql.execute("SELECT label.id, label.vintage, winery.name, label.name FROM label " +
                        "LEFT JOIN winery ON label.winery = winery.id " +
                        "ORDER BY winery.name, label.name, label.vintage").fetchall()

currentYear = date.today().year

# Probably don't need these, but generate them anyway..
allCosts = []
allBoldness = []
allHold = []

bottles = []
for label in labelData:
	blend = sql.execute("SELECT varietal.name, varietal.boldness, portion FROM blends " +
	                    "LEFT JOIN varietal ON blends.varietal = varietal.id " +
	                    "WHERE blends.label = ? " +
	                    "ORDER BY portion DESC", (label[0],)).fetchall()

	bottleData = sql.execute("SELECT id, cost, hold_until, boldness_coord, price_coord, hold_coord FROM bottle " +
	                         "WHERE label = ? " +
	                         "AND boldness_coord IS NOT NULL " +
	                         "AND price_coord IS NOT NULL " +
	                         "AND hold_coord IS NOT NULL " +
	                         "AND consumption IS NULL", (label[0],)).fetchall();

	weightedBoldness = sum([b[1] * b[2] / 100.0 for b in blend])

	for bottle in bottleData:
		allCosts.append(bottle[1])
		allBoldness.append(weightedBoldness)
		if (bottle[2] > currentYear):
			allHold.append(bottle[2])

		bottles.append({
			'id': bottle[0],
			'holdUntil': bottle[2],
			'cost': bottle[1],
			'boldness': weightedBoldness,
			'coord': (bottle[3], bottle[4], bottle[5]),
			'labelDescription': str(label[1]) + ' ' + label[2] + ' ' + label[3]
		})

layout = buildLayout(allCosts, allBoldness, allHold)
for bottle in bottles:
	addExistingBottle(layout, bottle)

# --------------------

rows = NumCostLevels * (NumHoldLevels + 1)
cols = NumBoldLevels + 2
outputTable = [["" for c in range(0, cols)] for r in range(0, rows)]
outputStyle = [["" for c in range(0, cols)] for r in range(0, rows)]

outputTable[0][0] = "Cost"
outputTable[0][1] = "Hold"

outputStyle[0][0] = Style.BRIGHT
outputStyle[0][1] = Style.BRIGHT

holdLabels = ["Drink Now"]
# Label the Holds
for idx, h in enumerate(layout['holdThresholds']):
	if (idx == NumHoldLevels - 2):
		holdLabels.append('Hold Longer')

	else:
		holdLabels.append('Hold < %d' % h)

# Label the Boldness
for idx, b in enumerate(layout['boldnessThresholds']):
	outputTable[0][idx + 2] = ("Boldness > %.0f" % -b)
	outputStyle[0][idx + 2] = Style.BRIGHT

# Label the Costs
for idx, c in enumerate(layout['costThresholds']):
	outputTable[(NumCostLevels - idx - 1) * (NumHoldLevels + 1) + 1][0] = ("< $%.0f" % c)
	outputStyle[(NumCostLevels - idx - 1) * (NumHoldLevels + 1) + 1][0] = Fore.GREEN

	for hidx, h in enumerate(holdLabels):
		outputTable[idx * (NumHoldLevels + 1) + NumHoldLevels - hidx][1] = h
		outputStyle[idx * (NumHoldLevels + 1) + NumHoldLevels - hidx][1] = Fore.BLUE

# Add the Bottles
for b in range(0, NumBoldLevels):
	for c in range(0, NumCostLevels):
		for h in range(0, NumHoldLevels):
			rowCoord = (NumCostLevels - c - 1) * (NumHoldLevels + 1) + NumHoldLevels - h
			colCoord = b + 2

			contents = layout['bottles'][b][c][h]
			if contents is None:
				outputTable[rowCoord][colCoord] = "        --------"
				outputStyle[rowCoord][colCoord] = Style.DIM

			else:
				outputTable[rowCoord][colCoord] = contents['labelDescription']

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
