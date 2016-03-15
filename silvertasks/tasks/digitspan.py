from psychopy import visual, core, event, gui, sound
from datetime import datetime
import random, numpy, sys, os

DATA_DIR = 'digitspan_data'
MONITOR = 'testMonitor' # should probably be a real one, not test
MONITOR_RESOLUTION = (1920, 1080) # default 800x600
SOUND_GENDER = 'female'

def run_task():
	if not os.path.isdir(DATA_DIR):
		try:
			os.mkdir(DATA_DIR)
		except (Exception e):
			print e.getMessage()
			print "Error: cannot create data directory: " + DATA_DIR
			sys.exit(1)

	while True:
		# tuple of form: (subject_id, test_number)
		subject_info = get_subject_info(sys.argv[1:])
		log_file = os.path.join(DATA_DIR, '_'.join(subject_info[0], subject_info[1]))

		if os.path.isfile(log_file):
			rename_dialog = gui.Dlg(title = 'Error: Log File Exists')
			rename_dialog.addText("A log file with the subject ID " + subject_info[0] +
				" and text number " + subject_info[1] + " already exists. Overwrite?")
			rename_dialog.show()

			if rename_dialog.OK:
				log_file = open(log_file, "w")
				break
			else:
				# not exactly necessary but w/e
				continue
		else:
			log_file = open(log_file)
			break

	# now log_file is a proper file

	sound_correct = sound.SoundPygame(value = 440, secs = 0.4)
	sound_incorrect = sound.SoundPygame(value = 330, secs = 0.4)
	sound_files = [fn for fn in os.listdir('sounds') if 
		fn.startswith(SOUND_GENDER) and fn.endswith('.mp3')]

	window = visual.window(MONITOR_RESOLUTION, monitor = MONITOR, units = 'deg', fullscr = True)






def get_subject_info(args = []):
	# no cli args
	if len(args) == 0:
		subject_info = gui.DlgFromDict(
			dictionary={'Subject ID': '', 'Test Number': '1'},
			title = 'Digit-Span Task')

		if (subject_info.OK):
			subject_id = subject_info.data[0].upper()
			subject_test_number = int(subject_info.data[1])
		else:
			sys.exit(1)
	# all args recvd
	elif len(args) == 2:
		subject_id = args[0].upper()
		subject_test_number = int(args[1])

	else:
		print "Usage: digitspan.py [subject_id] [subject_test_number]"
		sys.exit(1)

	return subject_id, subject_test_number

if __name__ == '__main__':
	run_task()