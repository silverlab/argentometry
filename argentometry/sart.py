from psychopy import visual, core, event, gui, sound
import random, numpy, sys, os
from datetime import datetime

class SART(object):
	def __init__(self, **kwargs):
		self.DIGIT_DISPLAY_TIME = kwargs.get('digit_display_time', 0.250)
		self.DIGIT_RANGE = kwargs.get('digit_range', (0, 9))
		self.DIGIT_SIZES = kwargs.get('digit_sizes', [1.8, 2.7, 3.5, 3.8, 4.5])
		self.TARGET_DIGIT = kwargs.get('target_digit', random.randint(*self.DIGIT_RANGE))
		self.NUM_DIGIT_SETS = kwargs.get('num_digit_sets', 25)
		self.MASK_TIME = kwargs.get('mask_time', 0.900)
		self.MASK_DIAMETER = kwargs.get('mask_diameter', 3.0)
		self.MAX_FAILS = kwargs.get('max_fails', 3)
		self.CORRECT_FREQ = kwargs.get('correct_freq', 440)
		self.WRONG_FREQ = kwargs.get('wrong_freq' 330)
		self.TONE_LENGTH = kwargs.get('tone_length', 0.5)
		self.PRACTICE_DIGIT_SETS = kwargs.get('practice_digit_sets', 2)
		self.DATA_DIR = kwargs.get('data_dir', 'sart_data')

		if not os.path.isdir(self.DATA_DIR):
			try:
				os.mkdir(self.DATA_DIR)
			except Exception as e:
				print e.getMessage()
				print "Error: cannot create data directory: " + self.DATA_DIR
				sys.exit(1)

			while True:
				subject_info = self.get_subject_info(sys.argv[1:])
				self.log_file = os.path.join(self.DATA_DIR, '_'.join(subject_info) + '.csv')

				if os.path.isfile(self.log_file):
					rename_dialog = gui.Dlg(title = 'Error: Log File Exists')
					rename_dialog.addText('A log file with this subject id ({0}) and test number {1} already exists. Overwrite?'.format(*subject_info))
					rename_dialog.show()

					if rename_dialog.OK:
						break
				else:
					break
				
			self.log_file = open(self.log_file, "w")

			self.data = []

			sound.init(48000, buffer = 126)

			# why convention different from digitspan? no clue
			self.sound_correct = sound.Sound(value = self.CORRECT_FREQ, secs = self.TONE_LENGTH)
			self.sound_incorrect = sound.Sound(value = self.WRONG_FREQ, secs = self.TONE_LENGTH)

			self.window = visual.Window([800, 600], monitor = 'testMonitor', units = 'cm', fullscr = True)
			self.mouse = event.Mouse(win = self.window)

			self.MASTER_CLOCK = core.Clock()
			self.TIMER = core.Clock()

			# run practice trial

			instructions = visual.TextStim(self.window, text = "Practice\n\nIn this task, a number will be shown on the screen. " +  
															   "If it is not {0}, then click your mouse anywhere on the screen. If it is a {0}, then do not click anywhere. ".format(self.TARGET_DIGIT) + 
															   "Please give equal importance to accuracy and speed.\n\nClick anywhere to continue.", wrapWidth = 40)

			instructions.draw()
			self.window.flip()

			# what??
			while 1 not in mouse.getPressed():
				pass
			while 1 in mouse.getPressed():
				pass

			visual.TextStim(self.window, text = "This is the sound of a correct response.").draw()
			self.window.flip()
			self.sound_correct.play()
			core.wait(2)
			visual.TextStim(self.window, text = "This is the sound of an incorrect response.").draw()
			self.window.flip()
			core.wait(2)

			# begin practice trial
			self.run_practice_trial()


			# run actual trial





	def get_subject_info(self, args = []):
        # no cli args
        if len(args) == 0:
            subject_info = gui.DlgFromDict(
                dictionary={'Subject ID': '', 'Test Number': '1'},
                title = 'SART Task')

            if (subject_info.OK):
                subject_id = subject_info.data[0].upper()
                subject_test_number = subject_info.data[1]
            else:
                sys.exit(1)
        # all args recvd
        elif len(args) == 2:
            subject_id = args[0].upper()
            subject_test_number = args[1]
        else:
            print "Usage: sart.py [subject_id] [test_number] -- Warning: functionality not guaranteed when called from CLI"
            sys.exit(1)

        return subject_id, subject_test_number

  	def run_practice_trial(self):									# undocumented params
  		mask1 = visual.Circle(self.window, radius = self.MASK_DIAMETER / 2, pos = [0.05, -0.39], lineWidth = 10)