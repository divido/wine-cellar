from colorama import Style

def stylize(fmt, value):
	return fmt + value + Style.RESET_ALL
