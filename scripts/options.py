#!/usr/bin/env python3

from colorama import Fore, Back, Style

import os, sys, getopt
from scripts.styling import stylize
import __main__ as main

# --------------------------------------------------------------------------------

def fmtShort(shortOpt, *args):
	"""Format a short option for the usage text"""
	fmt = stylize(Fore.BLUE, '-' + shortOpt)
	if len(args) > 0:
		fmt += ' ' + stylize(Fore.GREEN, args[0])
	return fmt

def fmtLong(longOpt, *args):
	"""Format a long option for the usage text"""
	fmt = stylize(Fore.BLUE, '--' + longOpt)
	if len(args) > 0:
		fmt += '=' + stylize(Fore.GREEN, args[0])
	return fmt

# ----------------------------------------

class OptionDefinition:
	"""This class maintains a running list of the option strings and the
	corresponding usage text to display the help. Simple and Parameterized
	options can be added, and the various fields will be updated in sync.
	"""

	def __init__(self):
		self.options = ''
		self.long_options = []
		self.usageHead = 'usage: ' + stylize(Style.BRIGHT, os.path.basename(main.__file__))
		self.usageOpts = []
		self.usageDesc = []
		self.maxLen = 0

	def addSimpleOption(self, shortOpt, longOpt, desc):
		"""This adds a simple option -- one that does not take any
		arguments. Must specify a short and long option, as well as a textual
		description of what the option does.
		"""

		self.options += shortOpt
		self.long_options.append(longOpt)

		optLen = len(longOpt)
		self.maxLen = max(self.maxLen, optLen)

		self.usageHead += ' ' + fmtShort(shortOpt)
		self.usageOpts.append((optLen, fmtShort(shortOpt) + ', ' + fmtLong(longOpt)))
		self.usageDesc.append(desc)

	def addParameterizedOption(self, shortOpt, longOpt, param, desc):
		"""This adds a parameterized options -- one that takes an additional
		argument. Beyond the short / long / desc (same as addSimpleOption), you
		must also specify the parameter name, which is used in the help text.
		"""

		self.options += shortOpt + ':'
		self.long_options.append(longOpt + '=')

		optLen = len(longOpt) + len(param) + 1
		self.maxLen = max(self.maxLen, optLen)

		self.usageHead += ' ' + fmtShort(shortOpt, param)
		self.usageOpts.append((optLen, fmtShort(shortOpt) + ', ' + fmtLong(longOpt, param)))
		self.usageDesc.append(desc)

	def usage(self):
		"""This constructs a usage block, suitable for printing to the screen."""

		usage = self.usageHead + '\n'
		for i in range(0, len(self.usageOpts)):
			(optLen, opt) = self.usageOpts[i]
			usage += '  ' + opt + (' ' * (self.maxLen - optLen))
			usage += '  ' + self.usageDesc[i] + '\n'

		return usage

# --------------------------------------------------------------------------------

def parseArguments(definitions):
	"""This parses the command line arguments based on the supplied
	definitions. The definitions are expected to be an array of tuples, each
	tuple either of these form:

	(shortOpt, longOpt, desc)
	(shortOpt, longOpt, param, desc)

	These arguments are provided to the OptionDefinition class depending on
	their type. The returned array will include the values for each definition,
	in the same order as the definitions were provided. Every three-value
	definition will get a True or False value (option present or not). Every
	four-value will get either None (option not present) or the parsed value as
	a string.
	"""

	optDef = OptionDefinition()
	optDef.addSimpleOption('h', 'help', 'Show this message')

	for defn in definitions:
		if len(defn) == 3:
			optDef.addSimpleOption(defn[0], defn[1], defn[2])

		elif len(defn) == 4:
			optDef.addParameterizedOption(defn[0], defn[1], defn[2], defn[3])

		else:
			raise Exception("Bad Argument Definition")

	# --------------------

	try:
		(optlist, args) = getopt.getopt(sys.argv[1:], optDef.options, optDef.long_options)

	except getopt.GetoptError as err:
		print(stylize(Fore.RED, str(err)) + '\n\n' + optDef.usage())
		sys.exit(1)

	for parsed in optlist:
		if parsed[0] == '-h' or parsed[0] == '--help':
			print(optDef.usage())
			sys.exit(0)

	# --------------------

	results = []
	for defn in definitions:
		optval = None
		for parsed in optlist:
			if parsed[0] == '-' + defn[0] or parsed[0] == '--' + defn[1]:
				optval = parsed[1]

		# For options without arguments, use True / False for present / absent
		# Otherwise, return the value (or None for absent)
		if len(defn) == 3:
			optval = (optval != None)

		results.append(optval)

	return results
