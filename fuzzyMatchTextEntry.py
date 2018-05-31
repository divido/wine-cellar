#!/usr/bin/env python3

import tty, sys, termios, os
from colorama import Fore, Back, Style
from fuzzywuzzy import fuzz

def _generateSuggestions(entry, completions):
	threshold = 70
	suggestions = [(item, fuzz.partial_ratio(entry.lower(), item.lower())) for item in list(set(completions))]
	return [suggestion[0] for suggestion in sorted(suggestions, key=lambda s: s[1], reverse=True) if suggestion[1] > threshold]

def textEntry(prompt, completions):
	oldSettings = termios.tcgetattr(sys.stdin.fileno())
	entry = ""
	selected = -1
	suggestions = []

	try:
		tty.setcbreak(sys.stdin.fileno())

		while True:
			lineWidth = int(os.popen('stty size', 'r').read().split()[1])

			leftPad = len(prompt) + len(entry) + 3;
			widthRemaining = lineWidth - leftPad;
			print('\r%s' % (' ' * leftPad), end='')

			for idx, suggestion in enumerate(suggestions):
				if len(suggestion) + 2 <= widthRemaining:
					widthRemaining -= len(suggestion) + 2
					style = Style.DIM

					if selected == idx:
						style = Style.BRIGHT + Back.BLUE

					print(style + (' %s ' % suggestion), end=Style.RESET_ALL)

			print(' ' * widthRemaining, end='')

			style = Style.BRIGHT if selected < 0 else ''
			print('\r%s%s' % (prompt, style + entry), end=Style.RESET_ALL)

			# --------------------

			ch = sys.stdin.read(1)

			if ch == '\n':
				# Look for accidental overlap with suggestions
				if selected < 0:
					for idx, suggestion in enumerate(suggestions):
						if suggestion.lower() == entry.lower():
							selected = idx

				# Now store the result, either entered or suggested
				result = entry if selected < 0 else suggestions[selected]
				selected = completions.index(result) if result in completions else None;

				print('\r%s%s%s' % (
					prompt, Style.BRIGHT + result,
					(' ' * (lineWidth - len(prompt) - len(result)))
				), end=Style.RESET_ALL)

				break

			else:
				if ch.isprintable():
					entry += ch
					selected = -1
					suggestions = _generateSuggestions(entry, completions)

				elif ord(ch) == 127:
					entry = entry[:len(entry) - 1]
					selected = -1
					suggestions = _generateSuggestions(entry, completions)

				elif ch == '\t':
					if len(suggestions) > 0:
						selected = (selected + 1) % len(suggestions)

				else:
					entry += "(" + str(ord(ch)) + ")"

	finally:
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, oldSettings)
		print()

	return (selected, result);
