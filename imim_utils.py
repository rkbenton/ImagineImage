# Print iterations progress
def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '',
                       decimals: int = 1, length: int = 100, fill: str = '█', print_end: str = "\r"):
    """
    Call in a loop to create terminal progress bar. Sample usage:

	import time

	# A thing we want progress on
	items = list(range(0, 57))
	l = len(items)

	# Initial call to print 0% progress
	print_progress_bar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	for i, item in enumerate(items):
	    # Do stuff...
	    time.sleep(0.1)
	    # Update Progress Bar
	    print_progress_bar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters

    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()
