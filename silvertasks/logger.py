import datetime, os

class Logger:
	logDir = ""
	logFile = ""
	logData = {}

	# files will be created relative to this module
	def __init__(self, logDir, logFileName, logFormat = "json"):
		if not os.path.isdir(logdir):
			os.mkdir(logDir)

		if not os.path.isfile(os.path.join(logdir, logFileName + "." + logFormat))

	def log(self, *args, **kwargs):
		kwargs['positional'] = args
		self.logData[str(datetime.datetime.now())] = kwargs
