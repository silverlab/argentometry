from psychopy import visual, core, event, gui, sound
from datetime import datetime
import random, numpy, sys, os

class DigitSpan:

	def __init__(self, **kwargs):
		self.DATA_DIR = kwargs.get('data_dir', 'digitspan_data')
		self.MONITOR = kwargs.get('monitor', 'testMonitor')
		self.MONITOR_RESOLUTION = kwargs.get('monitor_resolution', (1920, 1080))
		self.SOUND_GENDER = kwargs.get('sound_gender', 'female')
		self.N_PRACTICE_TRIALS = kwargs.get('practice_trials', 2)
		self.LEN_PRACTICE_TRIAL = kwargs.get('practice_trial_len', 3)
		self.DIGIT_DISPLAY_TIME = kwargs('digit_display_time', 0.500)

		if not os.path.isdir(self.DATA_DIR):
			try:
				os.mkdir(self.DATA_DIR)
			except (Exception e):
				print e.getMessage()
				print "Error: cannot create data directory: " + self.DATA_DIR
				sys.exit(1)

		while True:
			# tuple of form: (subject_id, test_number)
			self.subject_info = get_subject_info(sys.argv[1:])
			self.log_file = os.path.join(DATA_DIR, '_'.join(subject_info[0], subject_info[1]))

			if os.path.isfile(log_file):
				rename_dialog = gui.Dlg(title = 'Error: Log File Exists')
				rename_dialog.addText("A log file with the subject ID " + subject_info[0] +
					" and text number " + subject_info[1] + " already exists. Overwrite?")
				rename_dialog.show()

				if rename_dialog.OK:
					self.log_file = open(log_file, "w")
					break
				else:
					# not exactly necessary but w/e
					continue
			else:
				self.log_file = open(log_file)
				break

		# now log_file is a proper file

		self.sound_correct = sound.SoundPygame(value = 440, secs = 0.4)
		self.sound_incorrect = sound.SoundPygame(value = 330, secs = 0.4)
		self.sound_files = [sound.SoundPygame(value = fn) for fn in os.listdir('sounds') 
			if fn.startswith(SOUND_GENDER) and fn.endswith('.mp3')]
		self.sound_files.sort() # guarantee they are in order. Not exactly necessary

		# this is a bad way of doing this. Should load from a file.
		self.forward_sequences = [(9, 7),
								 (6, 3),
								 (5, 8, 2),
								 (6, 9, 4),
								 (7, 2, 8, 6),
								 (6, 4, 3, 9),
								 (4, 2, 7, 3, 1),
								 (7, 5, 8, 3, 6),
								 (3, 9, 2, 4, 8, 7),
								 (6, 1, 9, 4, 7, 3),
								 (4, 1, 7, 9, 3, 8, 6),
								 (6, 9, 1, 7, 4, 2, 8),
								 (3, 8, 2, 9, 6, 1, 7, 4),
								 (5, 8, 1, 3, 2, 6, 4, 7),
								 (2, 7, 5, 8, 6, 3, 1, 9, 4),
								 (7, 1, 3, 9, 4, 2, 5, 6, 8)]
		self.reverse_sequences = [(3, 1),
								 (2, 4),
								 (4, 6),
								 (5, 7),
								 (6, 2, 9),
								 (4, 7, 5),
								 (8, 2, 7, 9),
								 (4, 9, 6, 8),
								 (6, 5, 8, 4, 3),
								 (1, 5, 4, 8, 6),
								 (5, 3, 7, 4, 1, 8),
								 (7, 2, 4, 8, 5, 6),
								 (8, 1, 4, 9, 3, 6, 2),
								 (4, 7, 3, 9, 6, 2, 8),
								 (9, 4, 3, 7, 6, 2, 1, 8),
								 (7, 2, 8, 1, 5, 6, 4, 3)]

		# after this line executes, the window is showing.
		self.window = visual.window(MONITOR_RESOLUTION, monitor = MONITOR, units = 'deg', fullscr = True)
		self.mouse = event.Mouse(win = window)

	def run_task(self):
	
		visual.TextStim(window, text = "Practice" + "\n\n" +
									   "In this task, you will hear a sequence of numbers. When the " + 
									   "audio has finished, enter all of the numbers in the same " + 
									   "order as they were recited." + "\n\n" + 
									   "Press any key to continue.",
								wrapWidth = 30).draw()

		self.window.flip()

		event.waitKeys()
		visual.TextStim(window, text = "This is the sound of a correct response.").draw()
		self.window.flip()
		sound_correct.play()
		core.wait(2)
		visual.TextStim(window, text = "This is the sound of an incorrect response.").draw()
		self.window.flip()
		sound_incorrect.play()
		core.wait(2)

		for trial_num in range(self.N_PRACTICE_TRIALS):
			trial = random.sample(xrange(10), self.LEN_PRACTICE_TRIAL)
			for num in trial:



	def get_subject_info(self, args = []):
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

	def display_digit(self, digit):
		self.window.flip()
		self.sound_files[digit].setVolume(1)
		self.sound_files[digit].play()
		core.wait(self.DIGIT_DISPLAY_TIME) 


if __name__ == '__main__':
	ds = DigitSpan()
	ds.run_task()